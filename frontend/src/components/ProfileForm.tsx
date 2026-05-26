import { useEffect, useState } from "react";
import { Button, Center, Group, Stack, Text, Textarea, TextInput, Title } from "@mantine/core";
import { useForm } from "@mantine/form";

import { extractErrorMessage } from "@/api/errors";
import { useProfile, useUpdateProfile } from "@/hooks/useProfile";

const BIO_TEXTAREA_ROWS = 4;
const EMPTY_FIELD_PLACEHOLDER = "—";

type ProfileValues = { first_name: string; last_name: string; bio: string };

const isProfileEmpty = (profile: ProfileValues) =>
  !profile.first_name && !profile.last_name && !profile.bio;

export function ProfileForm() {
  const profileQuery = useProfile();
  const updateProfile = useUpdateProfile();
  const [mode, setMode] = useState<"view" | "edit">("edit");
  const [modeInitialized, setModeInitialized] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const form = useForm<ProfileValues>({
    initialValues: { first_name: "", last_name: "", bio: "" },
  });

  useEffect(() => {
    if (!profileQuery.data) return;
    form.setValues({
      first_name: profileQuery.data.first_name,
      last_name: profileQuery.data.last_name,
      bio: profileQuery.data.bio,
    });
    form.resetDirty();
    if (!modeInitialized) {
      setMode(isProfileEmpty(profileQuery.data) ? "edit" : "view");
      setModeInitialized(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profileQuery.data]);

  if (profileQuery.isLoading) {
    return <Text c="dimmed">Loading profile…</Text>;
  }
  if (profileQuery.isError || !profileQuery.data) {
    return <Text c="red">Failed to load profile.</Text>;
  }

  const handleSubmit = form.onSubmit(async (values) => {
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await updateProfile.mutateAsync(values);
      setStatusMessage("Saved");
      form.resetDirty();
      setMode("view");
    } catch (submissionError) {
      setErrorMessage(extractErrorMessage(submissionError, "Update failed"));
    }
  });

  const handleCancel = () => {
    form.setValues({
      first_name: profileQuery.data.first_name,
      last_name: profileQuery.data.last_name,
      bio: profileQuery.data.bio,
    });
    form.resetDirty();
    setErrorMessage(null);
    setStatusMessage(null);
    setMode("view");
  };

  if (mode === "view") {
    const profile = profileQuery.data;
    return (
      <Center>
        <Stack gap="sm" w="100%" maw={500}>
          <Title order={3}>Your profile</Title>
          <ProfileRow label="First name" value={profile.first_name} />
          <ProfileRow label="Last name" value={profile.last_name} />
          <ProfileRow label="Bio" value={profile.bio} />
          {statusMessage && <Text c="green">{statusMessage}</Text>}
          <Group>
            <Button onClick={() => { setStatusMessage(null); setMode("edit"); }}>Edit</Button>
          </Group>
        </Stack>
      </Center>
    );
  }

  return (
    <Center>
      <form onSubmit={handleSubmit} style={{ width: "100%", maxWidth: 500 }}>
        <Stack gap="sm">
          <Title order={3}>Your profile</Title>
          <TextInput label="First name" {...form.getInputProps("first_name")} />
          <TextInput label="Last name" {...form.getInputProps("last_name")} />
          <Textarea label="Bio" rows={BIO_TEXTAREA_ROWS} {...form.getInputProps("bio")} />
          {errorMessage && <Text c="red">{errorMessage}</Text>}
          <Group>
            <Button type="submit" loading={updateProfile.isPending}>Save</Button>
            <Button variant="default" onClick={handleCancel}>Cancel</Button>
          </Group>
        </Stack>
      </form>
    </Center>
  );
}

function ProfileRow({ label, value }: { label: string; value: string }) {
  return (
    <Stack gap={2}>
      <Text size="xs" c="dimmed">{label}</Text>
      <Text>{value || EMPTY_FIELD_PLACEHOLDER}</Text>
    </Stack>
  );
}
