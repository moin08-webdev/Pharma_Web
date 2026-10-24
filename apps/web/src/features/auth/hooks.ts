import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, setCsrfToken } from "@/lib/api";
import { SessionContext } from "./types";

export function useSession() {
  return useQuery({
    queryKey: ["session"],
    queryFn: async () => {
      try {
        const data = await apiFetch<SessionContext>("/api/v1/auth/me");
        setCsrfToken(data.csrf_token);
        return data;
      } catch (err: any) {
        setCsrfToken(null);
        return null;
      }
    },
    staleTime: 60 * 1000,
    retry: false,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const data = await apiFetch<SessionContext>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify(credentials),
      });
      setCsrfToken(data.csrf_token);
      return data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(["session"], data);
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await apiFetch("/api/v1/auth/logout", { method: "POST" });
      setCsrfToken(null);
    },
    onSuccess: () => {
      queryClient.setQueryData(["session"], null);
      queryClient.clear();
      window.location.href = "/login";
    },
  });
}
