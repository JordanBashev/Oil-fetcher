import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { Center, Loader } from "@mantine/core";

import { useSession } from "@/hooks/useSession";

const ADMIN_ROLE_NAME = "admin";

type RequireAdminProps = {
  children: ReactNode;
};

export function RequireAdmin({ children }: RequireAdminProps) {
  const { user, isLoading } = useSession();

  if (isLoading) {
    return (
      <Center h="100%">
        <Loader />
      </Center>
    );
  }
  if (!user) {
    return <Navigate to="/" replace />;
  }
  if (user.role !== ADMIN_ROLE_NAME) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
}
