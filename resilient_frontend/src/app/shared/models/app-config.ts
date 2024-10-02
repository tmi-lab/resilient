export interface DeviceField {
  fieldName: string;
  label: string;
  color: string;
  units: string;
  value?: string | number;
  hidden?: boolean;
}

export type DeviceType = 'scale' | 'sleep_mat' | 'scan_watch';

export interface ChartField {
  [key: string]: DeviceField[]
}

export interface AppConfig {
  apiUrl: string;
  chartFields: ChartField;
  nullReplaceValue: number;
}
