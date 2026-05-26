import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, PasswordInput, Stack, TextInput, Title } from "@mantine/core";
import { useForm } from "@mantine/form";

import { extractErrorMessage } from "@/api/errors";
import { useRegister } from "@/hooks/useRegister";

const POST_REGISTER_REDIRECT = "/dashboard";
const MIN_PASSWORD_LENGTH = 8;

export function RegisterForm() {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const navigate = useNavigate();
  const register = useRegister();

  const form = useForm({
    initialValues: { email: "", password: "", confirmPassword: "" },
    validate: {
      email: (value) => (/^\S+@\S+\.\S+$/.test(value) ? null : "Invalid email"),
      password: (value) =>
        value.length >= MIN_PASSWORD_LENGTH
          ? null
          : `Password must be at least ${MIN_PASSWORD_LENGTH} characters`,
      confirmPassword: (value, values) =>
        value === values.password ? null : "Passwords do not match",
    },
  });

  const handleSubmit = form.onSubmit(async (values) => {
    setErrorMessage(null);
    try {
      await register.mutateAsync({ email: values.email, password: values.password });
      navigate(POST_REGISTER_REDIRECT);
    } catch (submissionError) {
      setErrorMessage(extractErrorMessage(submissionError, "Registration failed"));
    }
  });

  return (
    <form onSubmit={handleSubmit}>
      <Stack gap="sm" maw={400}>
        <Title order={3}>Create account</Title>
        <TextInput label="Email" required {...form.getInputProps("email")} />
        <PasswordInput label="Password" required {...form.getInputProps("password")} />
        <PasswordInput label="Confirm password" required {...form.getInputProps("confirmPassword")} />
        {errorMessage && <div style={{ color: "var(--mantine-color-red-7)" }}>{errorMessage}</div>}
        <Button type="submit" loading={register.isPending}>Create account</Button>
      </Stack>
    </form>
  );
}
