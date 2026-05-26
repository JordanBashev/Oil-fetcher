import { useMutation, useQueryClient } from "@tanstack/react-query";

import { loginRequest, type AuthSuccess, type Credentials } from "@/api/auth";
import { SESSION_QUERY_KEY } from "./useSession";

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (credentials: Credentials) => loginRequest(credentials),
    onSuccess: (data: AuthSuccess) => {
      queryClient.setQueryData(SESSION_QUERY_KEY, data);
    },
  });
}
