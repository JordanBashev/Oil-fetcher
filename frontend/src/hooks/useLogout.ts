import { useMutation, useQueryClient } from "@tanstack/react-query";

import { logoutRequest } from "@/api/auth";
import { SESSION_QUERY_KEY } from "./useSession";

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: logoutRequest,
    onSuccess: () => {
      queryClient.clear();
      queryClient.setQueryData(SESSION_QUERY_KEY, null);
    },
  });
}
