"use client"

import MainLayout from "@/components/main-layout"

export default function MainRouteLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return <MainLayout>{children}</MainLayout>
}
