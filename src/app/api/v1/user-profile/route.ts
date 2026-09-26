import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET() {
  return NextResponse.json({
    status: "success",
    route: "/api/v1/user-profile",
    profile: {
      role: "tenant",
      status: "active",
      features: ["deposit_rescue", "statutory_audit"],
    },
  });
}
