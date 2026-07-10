const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SyncedUser {
  access_token: string;
  user_id: string;
  email: string;
  name?: string | null;
  avatar_url?: string | null;
}

export async function syncGoogleUser(input: {
  email: string;
  google_id: string;
  name?: string | null;
  picture?: string | null;
}): Promise<SyncedUser> {
  const res = await fetch(`${API_URL}/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: input.email,
      google_id: input.google_id,
      name: input.name,
      picture: input.picture,
    }),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to sync user: ${res.status}`);
  }
  return res.json();
}
