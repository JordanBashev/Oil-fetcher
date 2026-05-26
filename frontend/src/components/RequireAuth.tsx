import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { Center, Loader } from "@mantine/core";

import { useSession } from "@/hooks/useSession";

type RequireAuthProps = {
  children: ReactNode;
};

export function RequireAuth({ children }: RequireAuthProps) {
  const { isAuthenticated, isLoading } = useSession();

  if (isLoading) {
    return (
      <Center h="100%">
        <Loader />
      </Center>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}
