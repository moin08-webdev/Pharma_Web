import React from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import { WorkspaceLayout } from "@/layouts/WorkspaceLayout";
import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { PrescriptionsPage } from "@/pages/PrescriptionsPage";
import { NewPrescriptionPage } from "@/pages/NewPrescriptionPage";
import { PrescriptionReviewPage } from "@/pages/PrescriptionReviewPage";
import { PrescriptionPlanPage } from "@/pages/PrescriptionPlanPage";
import { MedicineSearchPage } from "@/pages/MedicineSearchPage";
import { MedicineDetailPage } from "@/pages/MedicineDetailPage";
import { InventoryPage } from "@/pages/InventoryPage";
import { ApprovalsPage } from "@/pages/ApprovalsPage";
import { OrdersPage } from "@/pages/OrdersPage";
import { OrderDetailPage } from "@/pages/OrderDetailPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { PrivacyPage } from "@/pages/PrivacyPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/privacy",
    element: <PrivacyPage />,
  },
  {
    path: "/app",
    element: <WorkspaceLayout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: "prescriptions",
        element: <PrescriptionsPage />,
      },
      {
        path: "prescriptions/new",
        element: <NewPrescriptionPage />,
      },
      {
        path: "prescriptions/:id/review",
        element: <PrescriptionReviewPage />,
      },
      {
        path: "prescriptions/:id/plan",
        element: <PrescriptionPlanPage />,
      },
      {
        path: "medicines",
        element: <MedicineSearchPage />,
      },
      {
        path: "medicines/:id",
        element: <MedicineDetailPage />,
      },
      {
        path: "inventory",
        element: <InventoryPage />,
      },
      {
        path: "approvals",
        element: <ApprovalsPage />,
      },
      {
        path: "orders",
        element: <OrdersPage />,
      },
      {
        path: "orders/:id",
        element: <OrderDetailPage />,
      },
      {
        path: "settings",
        element: <SettingsPage />,
      },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
