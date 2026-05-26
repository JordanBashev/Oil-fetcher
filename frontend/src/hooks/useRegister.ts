import { useMutation, useQueryClient } from "@tanstack/react-query";

import { registerRequest, type AuthSuccess, type Credentials } from "@/api/auth";
import { SESSION_QUERY_KEY } from "./useSession";

export function useRegister() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (credentials: Credentials) => registerRequest(credentials),
    onSuccess: (data: AuthSuccess) => {
      queryClient.clear();
      queryClient.setQueryData(SESSION_QUERY_KEY, data);
    },
  });
}
