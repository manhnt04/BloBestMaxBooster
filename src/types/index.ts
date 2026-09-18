export type PerformanceMode = 'beast' | 'esports' | 'eco';

export interface GameItem {
  id: string;
  packageName: string;
  name: string;
  icon: string;
  isGame: boolean;
  sizeMB: number;
  targetFps: number;
  isBoosted: boolean;
  schemes?: string[];
  nativeStoreUrl?: string;
  publisher?: string;
}

export interface DeviceSpecs {
  manufacturer: string;
  model: string;
  brand: string;
  board: string;
  hardware: string;
  osName: string;
  osVersion: string;
  coreCount: number;
  totalMemoryGB: number;
  totalStorageGB: number;
  freeStorageGB: number;
  cpuArchitecture: string;
}

export interface LiveNetworkState {
  type: string;
  isConnected: boolean;
  isInternetReachable: boolean;
  ipAddress: string;
  pingMs: number;
  jitterMs: number;
}

export interface BatteryInfo {
  batteryPercent: number;
  isCharging: boolean;
  isLowPowerMode: boolean;
  stateLabel: string;
  voltageVolts: number;
}

export interface BoostBenchmarkResult {
  deviceModel: string;
  networkType: string;
  pingBeforeMs: number;
  pingAfterMs: number;
  pingDropMs: number;
  jitterMs: number;
  batteryPercent: number;
  freeStorageGB: number;
  totalMemoryGB: number;
  modeApplied: string;
}

export interface SystemStats {
  ramUsedPercent: number;
  ramTotalGB: number;
  ramUsedGB: number;
  freeStorageGB: number;
  totalStorageGB: number;
  cpuPercent: number;
  pingMs: number;
  jitterMs: number;
  batteryPercent: number;
  networkType: string;
  ipAddress: string;
  isCharging: boolean;
  isLowPowerMode: boolean;
  fpsEstimate: number;
  isHyperBoosted: boolean;
  lastBenchmark?: BoostBenchmarkResult;
}

export interface GamingTool {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  enabled: boolean;
  color: string;
  badge?: string;
}