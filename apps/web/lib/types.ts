export interface Brief {
  id: string;
  user_id: string;
  brand_name: string;
  brief_text: string;
  reference_image_key?: string;
  status: "pending" | "running" | "done" | "failed";
  created_at: string;
}

export interface Run {
  id: string;
  brief_id: string;
  parent_run_id?: string;
  status: "queued" | "running" | "succeeded" | "failed";
  started_at?: string;
  finished_at?: string;
  total_cost_usd?: string;
}

export interface RunStep {
  id: string;
  step_name: string;
  provider?: string;
  model?: string;
  status: string;
  fallback_triggered: boolean;
  cost_usd?: string;
  latency_ms?: number;
  manifest_key?: string;
  asset_key?: string;
}

export interface Variant {
  id: string;
  asset_key: string;
  thumbnail_key?: string;
  manifest_key: string;
  sha256_hash: string;
  provider_summary?: string;
  selected: boolean;
}

export interface RunDetail extends Run {
  steps: RunStep[];
  variants: Variant[];
}

export interface VerifyResult {
  match: boolean;
  expected_sha256: string;
  actual_sha256: string;
  manifest_key: string;
  verified_at: string;
}
