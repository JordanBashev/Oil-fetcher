import { AppShell, Burger, Button, Group, NavLink, Stack, Text, Title } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useLocation, useNavigate } from "react-router-dom";

import { useLogout } from "@/hooks/useLogout";
import { useSession } from "@/hooks/useSession";

const ADMIN_ROLE_NAME = "admin";
const NAV_WIDTH = 240;
const HEADER_HEIGHT = 60;

type NavItem = { label: string; path: string; adminOnly?: boolean };

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Forecasts", path: "/forecasts" },
  { label: "Profile", path: "/profile" },
  { label: "Admin · Users", path: "/admin/users", adminOnly: true },
  { label: "Admin · Logs", path: "/admin/logs", adminOnly: true },
];

type AppLayoutProps = { children: React.ReactNode };

export function AppLayout({ children }: AppLayoutProps) {
  const [navOpened, { toggle: toggleNav, close: closeNav }] = useDisclosure();
  const { user } = useSession();
  const logout = useLogout();
  const navigate = useNavigate();
  const location = useLocation();

  const isAdmin = user?.roles.includes(ADMIN_ROLE_NAME) ?? false;
  const visibleItems = NAV_ITEMS.filter((item) => !item.adminOnly || isAdmin);

  const handleLogout = async () => {
    await logout.mutateAsync();
    navigate("/");
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    closeNav();
  };

  return (
    <AppShell
      header={{ height: HEADER_HEIGHT }}
      navbar={{ width: NAV_WIDTH, breakpoint: "sm", collapsed: { mobile: !navOpened } }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={navOpened} onClick={toggleNav} hiddenFrom="sm" size="sm" />
            <Title order={4}>Oil Forecasts</Title>
          </Group>
          {user && (
            <Group gap="sm">
              <Text size="sm" c="dimmed">
                {user.email}
              </Text>
              <Button size="xs" variant="default" onClick={handleLogout} loading={logout.isPending}>
                Sign out
              </Button>
            </Group>
          )}
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Stack gap={4}>
          {visibleItems.map((item) => (
            <NavLink
              key={item.path}
              label={item.label}
              active={location.pathname === item.path}
              onClick={() => handleNavigate(item.path)}
            />
          ))}
        </Stack>
      </AppShell.Navbar>

      <AppShell.Main>{children}</AppShell.Main>
    </AppShell>
  );
}
