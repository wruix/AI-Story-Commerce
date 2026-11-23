"use client"

import { usePathname } from "next/navigation"
import Navigation from "@/components/navigation"

export default function MainLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const pathname = usePathname()

  return (
    <div className="flex h-screen overflow-hidden">
      <Navigation />
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 border-b border-gray-200 bg-white px-6 flex items-center justify-between">
          <div className="text-lg font-semibold text-gray-900">
            AI Story Commerce — 内部生产管理系统
          </div>
          <div className="text-sm text-gray-500">
            {pathname === "/dashboard" ? "工作台" : pathname.replace("/", "") || "首页"}
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
          {children}
        </main>
      </div>
    </div>
  )
}
