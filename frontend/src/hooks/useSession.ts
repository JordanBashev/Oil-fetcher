import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { refreshRequest, type AuthSuccess } from "@/api/auth";
import { onSessionInvalidated } from "@/api/client";

export const SESSION_QUERY_KEY = ["session"] as const;

export function useSession() {
  const queryClient = useQueryClient();
  const query = useQuery<AuthSuccess | null>({
    queryKey: SESSION_QUERY_KEY,
    queryFn: async () => {
      try {
        return await refreshRequest();
      } catch {
        return null;
      }
    },
    retry: false,
  });

  useEffect(() => {
    return onSessionInvalidated(() => {
      queryClient.setQueryData<AuthSuccess | null>(SESSION_QUERY_KEY, null);
    });
  }, [queryClient]);

  return {
    user: query.data?.user ?? null,
    isLoading: query.isLoading,
    isAuthenticated: !!query.data?.user,
  };
}
