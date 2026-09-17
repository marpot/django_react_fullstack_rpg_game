import { expect, test } from "@playwright/test";

test("register, select a character, create a room and start a game", async ({ page }) => {
  const username = `slice_${Date.now()}`;
  const roomName = `Slice room ${username}`;
  const password = "Slice-test-password-123";

  await page.goto("/register");
  await page.getByPlaceholder("Nazwa użytkownika").fill(username);
  await page.getByPlaceholder("Email").fill(`${username}@example.test`);
  await page.getByPlaceholder("Hasło").fill(password);
  await page.getByRole("button", { name: "Rozpocznij przygodę" }).click();
  await expect(page).toHaveURL(/\/$/);

  await page.getByPlaceholder("Nazwa użytkownika").fill(username);
  await page.getByPlaceholder("Hasło").fill(password);
  await page.getByRole("button", { name: "Zaloguj się" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole("button", { name: "Karta bohatera" }).click();
  await expect(page.getByRole("heading", { name: "Aktywna postać" })).toBeVisible();
  const character = page.locator(".character-card").filter({ hasText: `${username}_hero` });
  await expect(character).toBeVisible();
  await character.click();
  await expect(character).toHaveClass(/active/);

  await page.getByRole("link", { name: "Wróć do Sali Przygód" }).click();
  await page.getByRole("button", { name: "Nowa wyprawa" }).click();
  await page.getByLabel("Nazwa pokoju").fill(roomName);
  await page.getByRole("button", { name: "Utwórz pokój" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByText(roomName, { exact: true }).click();
  await expect(page.getByRole("heading", { name: roomName })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Drużyna" })).toBeVisible();
  await expect(page.getByText(`${username}_hero`).first()).toBeVisible();

  await page.getByRole("button", { name: /Generuj przygodę/ }).click();
  const start = page.getByRole("button", { name: "Rozpocznij przygodę" });
  await expect(start).toBeEnabled();
  await start.click();

  await expect(page.locator(".gameWindow")).toBeVisible();
  await expect(page.getByText("ELDORIA", { exact: false })).toBeVisible();
});
