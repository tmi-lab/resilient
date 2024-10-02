import { Icon } from "@shared/models/icons";

export const ICONS: { [key: string]: Icon } = {
  scale: {
    id: 'scale',
    path: 'assets/icons/devices_scale.svg',
    prettyName: 'Scale',
    summaryUrl: 'scales/',
    summaryName: 'scales'
  },
  sleep_mat: {
    id: 'sleepmat',
    path: 'assets/icons/devices_bed.svg',
    prettyName: 'Sleepmat',
    summaryUrl: 'sleepmats/summary/',
    summaryName: 'sleepmats_summary'
  },
  scan_watch: {
    id: 'scan_watch',
    path: 'assets/icons/devices_clock.svg',
    prettyName: 'Scan Watch',
    summaryUrl: 'scanwatches/summary/',
    summaryName: 'scanwatches_summary'

  },
  usage_level: {
    id: 'usage_level',
    path: 'assets/icons/usage_level.svg',
    prettyName: 'Usage Level'
  },
  usage_battery: {
    id: 'usage_battery',
    path: 'assets/icons/usage_battery.svg',
    prettyName: 'Usage Battery'
  },
  usage_active: {
    id: 'usage_active',
    path: 'assets/icons/usage_active.svg',
    prettyName: 'Active'
  },
  usage_inactive: {
    id: 'usage_inactive',
    path: 'assets/icons/usage_inactive.svg',
    prettyName: 'Inactive'
  }

};
