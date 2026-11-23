"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  FolderKanban,
  FileText,
  Users,
  BarChart3,
  Video,
  Image,
  CheckCircle2,
  AlertCircle,
  LayoutGrid,
  Settings,
  Package,
} from "lucide-react"

const navigation = [
  { name: "工作台", href: "/dashboard", icon: LayoutDashboard },
  { name: "项目列表", href: "/projects", icon: FolderKanban },
  { name: "商品库", href: "/products", icon: Package },
  { name: "客户管理", href: "/customers", icon: Users },
  { name: "剧情创意库", href: "/story-ideas", icon: FileText },
  { name: "剧本编辑器", href: "/scripts", icon: FileText },
  { name: "人物管理", href: "/characters", icon: Users },
  { name: "分镜管理", href: "/storyboards", icon: LayoutGrid },
  { name: "视频生产中心", href: "/production-tasks", icon: Video },
  { name: "素材库", href: "/media-assets", icon: Image },
  { name: "广告审核", href: "/compliance-reviews", icon: CheckCircle2 },
  { name: "发布记录", href: "/publishing-records", icon: Video },
  { name: "数据分析", href: "/performance-metrics", icon: BarChart3 },
  { name: "Prompt模板", href: "/prompt-templates", icon: FileText },
  { name: "操作审计", href: "/audit-logs", icon: AlertCircle },
]

export default function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="fixed left-0 top-0 h-screen w-64 bg-white border-r border-gray-200">
      <div className="h-full flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white font-bold">
              AI
            </div>
            <span className="font-semibold text-gray-900">AI Story Commerce</span>
          </Link>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-blue-50 text-blue-600"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.name}
              </Link>
            )
          })}
        </div>
        <div className="p-4 border-t border-gray-200">
          <Link
            href="/settings"
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
          >
            <Settings className="w-4 h-4" />
            设置
          </Link>
        </div>
      </div>
    </nav>
  )
}
