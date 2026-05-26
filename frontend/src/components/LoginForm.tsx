import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, PasswordInput, Stack, TextInput, Title } from "@mantine/core";
import { useForm } from "@mantine/form";

import { extractErrorMessage } from "@/api/errors";
import { useLogin } from "@/hooks/useLogin";

const POST_LOGIN_REDIRECT = "/dashboard";

export function LoginForm() {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const navigate = useNavigate();
  const login = useLogin();

  const form = useForm({
    initialValues: { email: "", password: "" },
    validate: {
      email: (value) => (/^\S+@\S+\.\S+$/.test(value) ? null : "Invalid email"),
      password: (value) => (value.length > 0 ? null : "Password is required"),
    },
  });

  const handleSubmit = form.onSubmit(async (values) => {
    setErrorMessage(null);
    try {
      await login.mutateAsync(values);
      navigate(POST_LOGIN_REDIRECT);
    } catch (submissionError) {
      setErrorMessage(extractErrorMessage(submissionError, "Login failed"));
    }
  });

  return (
    <form onSubmit={handleSubmit}>
      <Stack gap="sm" maw={400}>
        <Title order={3}>Log in</Title>
        <TextInput label="Email" required {...form.getInputProps("email")} />
        <PasswordInput label="Password" required {...form.getInputProps("password")} />
        {errorMessage && <div style={{ color: "var(--mantine-color-red-7)" }}>{errorMessage}</div>}
        <Button type="submit" loading={login.isPending}>Log in</Button>
      </Stack>
    </form>
  );
}
