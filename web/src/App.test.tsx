import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { App } from "./App";

test("mostra o título Quadralug", () => {
  render(<App />);

  const title = screen.getByRole("heading", { level: 1, name: "Quadralug" });

  expect(title).toBeTruthy();
});
