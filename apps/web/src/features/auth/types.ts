export interface User {
  id: string;
  email: string;
  role: "ADMIN" | "PHARMACIST" | "ASSISTANT";
  active: boolean;
}

export interface Pharmacy {
  id: string;
  name: string;
  timezone: string;
  currency: string;
  demo_mode: boolean;
  expiry_buffer_days: number;
  settings_version: number;
}

export interface SessionContext {
  user: User;
  pharmacy: Pharmacy;
  csrf_token: string;
  permissions: string[];
}
