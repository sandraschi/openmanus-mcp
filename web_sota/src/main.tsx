import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import { LoggerProvider } from "@/contexts/LoggerContext";

import App from "./App";
import "./index.css";

const savedTheme = localStorage.getItem("openmanus-theme");
if (savedTheme === "light") {
  document.documentElement.classList.remove("dark");
} else {
  document.documentElement.classList.add("dark");
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <LoggerProvider>
        <App />
      </LoggerProvider>
    </BrowserRouter>
  </StrictMode>,
);
