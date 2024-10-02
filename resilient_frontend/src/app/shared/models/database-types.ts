export interface User {
  id: string;
  username: string;
  role: string;
  updated_at: string;
  created_at: string;
  active: boolean;
}

export interface Users {
  users: User[];
}

export interface Device {
  id: string;
  user: string;
  device_hash: string;
  device_type: string;
  mac_address: string;
  is_active: string;
  created_at: string;
  updated_at: string;
}

export interface Devices {
  devices: Devices[];
}
