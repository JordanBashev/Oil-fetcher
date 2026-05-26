import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getProfileRequest, updateProfileRequest, type Profile, type ProfileUpdate } from "@/api/auth";

const PROFILE_QUERY_KEY = ["profile"] as const;

export function useProfile() {
  return useQuery<Profile>({
    queryKey: PROFILE_QUERY_KEY,
    queryFn: getProfileRequest,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (changes: ProfileUpdate) => updateProfileRequest(changes),
    onSuccess: (updated: Profile) => {
      queryClient.setQueryData(PROFILE_QUERY_KEY, updated);
    },
  });
}
