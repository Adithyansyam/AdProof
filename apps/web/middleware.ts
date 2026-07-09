export { default } from "next-auth/middleware";

export const config = {
  matcher: ["/dashboard/:path*", "/brief/:path*", "/library/:path*", "/run/:path*"],
};
