import { useState } from "react";
import { Navigate } from "react-router-dom";
import { Center, Loader, SegmentedControl, Stack } from "@mantine/core";

import { LoginForm } from "@/components/LoginForm";
import { RegisterForm } from "@/components/RegisterForm";
import { useSession } from "@/hooks/useSession";

const AUTH_MODE_LOGIN = "login";
const AUTH_MODE_REGISTER = "register";
type AuthMode = typeof AUTH_MODE_LOGIN | typeof AUTH_MODE_REGISTER;

const AUTH_OPTIONS = [
  { label: "Log in", value: AUTH_MODE_LOGIN },
  { label: "Register", value: AUTH_MODE_REGISTER },
];

export function HomePage() {
  const { isAuthenticated, isLoading } = useSession();
  const [authMode, setAuthMode] = useState<AuthMode>(AUTH_MODE_LOGIN);

  if (isLoading) {
    return (
      <Center h="100%">
        <Loader />
      </Center>
    );
  }
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <Center h="100vh" p="md">
      <Stack gap="md" w={400}>
        <SegmentedControl
          value={authMode}
          onChange={(nextValue) => setAuthMode(nextValue as AuthMode)}
          data={AUTH_OPTIONS}
        />
        {authMode === AUTH_MODE_LOGIN ? <LoginForm /> : <RegisterForm />}
      </Stack>
    </Center>
  );
}
