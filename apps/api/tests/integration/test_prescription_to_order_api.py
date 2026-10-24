import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_complete_prescription_to_order_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login as Pharmacist
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "pharmacist@pharmabridge.demo", "password": "DemoPharmacistPass123!"},
        )
        assert login_res.status_code == 200

        # 2. Search medicine Brand A
        med_res = await client.get("/api/v1/medicines?q=Brand A")
        assert med_res.status_code == 200
        meds = med_res.json()
        assert len(meds) > 0
        brand_a = meds[0]

        # 3. Create a new draft prescription
        rx_create_res = await client.post(
            "/api/v1/prescriptions",
            json={"optional_patient_reference": "E2E-PATIENT-101"},
        )
        assert rx_create_res.status_code == 201
        rx = rx_create_res.json()
        rx_id = rx["id"]
        assert rx["status"] == "draft"

        # 4. Add medicine line: Brand A Paracetamol, requested quantity 15
        line_payload = {
            "expected_revision": rx["revision"],
            "lines": [
                {
                    "raw_name": brand_a["brand_name"],
                    "raw_strength": "500 mg",
                    "selected_product_id": brand_a["id"],
                    "requested_quantity": 15,
                    "quantity_unit": "tablet",
                    "confirmation_state": "confirmed",
                }
            ],
        }
        update_lines_res = await client.put(f"/api/v1/prescriptions/{rx_id}/lines", json=line_payload)
        assert update_lines_res.status_code == 200
        updated_rx = update_lines_res.json()
        assert len(updated_rx["lines"]) == 1

        # 5. Confirm prescription
        confirm_res = await client.post(f"/api/v1/prescriptions/{rx_id}/confirm")
        assert confirm_res.status_code == 200
        confirmed_rx = confirm_res.json()
        assert confirmed_rx["status"] == "confirmed"

        # 6. Check formulation candidates for Brand A
        cand_res = await client.get(f"/api/v1/medicines/{brand_a['id']}/candidates")
        assert cand_res.status_code == 200
        cand_data = cand_res.json()
        assert len(cand_data["eligible_candidates"]) > 0
        product_b = cand_data["eligible_candidates"][0]
        assert "Product B" in product_b["brand_name"]
        assert product_b["is_local_stock_confirmed"] is True

        # 7. Create fulfilment plan
        plan_create_res = await client.post("/api/v1/plans", json={"prescription_id": rx_id})
        assert plan_create_res.status_code == 201
        plan = plan_create_res.json()
        plan_id = plan["id"]
        assert plan["state"] == "draft"
        assert len(plan["lines"]) == 1
        plan_line_id = plan["lines"][0]["id"]

        # Initial quote (Brand A as prescribed)
        quote_1 = plan["current_quote"]
        assert quote_1 is not None
        assert quote_1["finalizable"] is True
        assert quote_1["coverage"]["fulfilled_lines"] == 1

        # 8. Switch line to candidate Product B
        select_cand_res = await client.patch(
            f"/api/v1/plans/{plan_id}/lines/{plan_line_id}",
            json={
                "selected_product_id": product_b["product_id"],
                "selection_reason": "candidate_selected_savings",
                "authorization_required": False,
                "expected_plan_version": plan["version"],
            },
        )
        assert select_cand_res.status_code == 200
        updated_plan = select_cand_res.json()
        quote_2 = updated_plan["current_quote"]
        assert quote_2 is not None
        # Product B whole pack dispensing: 2 packs of 10 = 20 tablets, cost 2000 paise vs baseline 3000 paise
        # Difference = 33.33%
        assert quote_2["totals"]["comparable_subset_difference_percent"] == "33.33"
        assert quote_2["finalizable"] is True

        # 9. Assistant tries to approve -> must fail with 403 Forbidden
        async with AsyncClient(transport=transport, base_url="http://test") as assistant_client:
            await assistant_client.post(
                "/api/v1/auth/login",
                json={"email": "assistant@pharmabridge.demo", "password": "DemoAssistantPass123!"},
            )
            blocked_appr_res = await assistant_client.post(
                f"/api/v1/plans/{plan_id}/approvals",
                json={
                    "quote_id": quote_2["quote_id"],
                    "decision": "APPROVED",
                    "reason": "Assistant attempting approval",
                },
            )
            assert blocked_appr_res.status_code == 403
            assert blocked_appr_res.json()["error"]["code"] == "FORBIDDEN"

        # 10. Pharmacist approves plan
        appr_res = await client.post(
            f"/api/v1/plans/{plan_id}/approvals",
            json={
                "quote_id": quote_2["quote_id"],
                "decision": "APPROVED",
                "reason": "Clinical formulation verified, patient accepted generic savings.",
            },
        )
        assert appr_res.status_code == 200
        approved_plan = appr_res.json()
        assert approved_plan["state"] == "approved"
        approval_id = approved_plan["approval"]["id"]

        # 11. Finalize Order with Idempotency Key
        idempotency_key = f"IDEM-{uuid.uuid4()}"
        finalize_res = await client.post(
            "/api/v1/orders",
            json={
                "quote_id": quote_2["quote_id"],
                "approval_id": approval_id,
            },
            headers={"Idempotency-Key": idempotency_key},
        )
        assert finalize_res.status_code == 201
        order = finalize_res.json()
        assert "ORD-" in order["order_number"]
        assert order["total_paise"] == 2000
        assert len(order["lines"]) == 1
        order_line = order["lines"][0]
        assert order_line["dispensed_product_name"] == product_b["brand_name"]
        assert order_line["supplied_quantity"] == 20  # whole pack allocation (2 packs * 10)
        assert len(order_line["allocations"]) > 0

        # 12. Idempotent Retry: same key and payload returns identical order
        retry_res = await client.post(
            "/api/v1/orders",
            json={
                "quote_id": quote_2["quote_id"],
                "approval_id": approval_id,
            },
            headers={"Idempotency-Key": idempotency_key},
        )
        assert retry_res.status_code in (200, 201)
        assert retry_res.json()["id"] == order["id"]

        # 13. Idempotent Conflict: same key with different payload returns 409
        conflict_res = await client.post(
            "/api/v1/orders",
            json={
                "quote_id": str(uuid.uuid4()),
                "approval_id": approval_id,
            },
            headers={"Idempotency-Key": idempotency_key},
        )
        assert conflict_res.status_code == 409
        assert conflict_res.json()["error"]["code"] == "CONFLICT"

        # 14. Verify prescription is now COMPLETED
        final_rx_res = await client.get(f"/api/v1/prescriptions/{rx_id}")
        assert final_rx_res.status_code == 200
        assert final_rx_res.json()["status"] == "completed"

        # 15. Verify CSV export works
        csv_res = await client.get(f"/api/v1/orders/{order['id']}/export?format=csv")
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.headers["content-type"]
        assert order["order_number"] in csv_res.text
