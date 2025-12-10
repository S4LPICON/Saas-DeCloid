export interface Server {
  server_uuid: string;
  name: string;
  status: string;
  artifact: string;
  ip_address: string;
  port: number;
  players_online?: number;
  max_players?: number;
  cpu_allocated?: number;
  memory_allocated?: number;
  last_seen?: string | null;
  create_date?: string;
  uptime?: number;
  owner?: number;
  node?: string;
}

export interface Node {
  node_uuid: string;
  key: string;
  name: string;
  ip_address: string;
  location: string;
  api_token: string;
  status: string;
  cpu_cores: number;
  cpu_usage: number;
  cpu_over_allocation: number;
  memory: number;
  memory_usage: number;
  memory_over_allocation: number;
  storage: number;
  storage_usage: number;
  storage_over_allocation: number;
  daemon_version?: string | null;
  docker_version?: string | null;
  last_seen?: string | null;
  created_at: string;
  daemon_port: number;
  daemon_sftp_port: number;
  last_heartbeat?: string | null;
  is_online: boolean;
  servers?: Server[];
  owner?: number;
}

export interface Artifact {
  artifact_uuid: string;
  name: string;
  version: string;
  description: string;
  type: string;
  status: string;
  java_version: string;
  mc_version: string;
  size_in_mb: number;
  cpu_cores: number;
  memory_in_mb: number;
  zip_file: string;
  registry_path: string;
  dockerfile_name: string;
  dockerfile_custom?: string | null;
  logs: string;
  active_instances: number;
  creation_date: string;
  update_date: string;
  owner?: number;
}
