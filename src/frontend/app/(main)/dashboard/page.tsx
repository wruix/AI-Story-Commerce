"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  LayoutDashboard,
  FolderKanban,
  FileText,
  Users,
  BarChart3,
  CheckCircle2,
  Plus,
} from "lucide-react"

const stats = [
  { label: "项目总数", value: "0", icon: LayoutDashboard, color: "text-blue-600" },
  { label: "商品资料", value: "0", icon: FolderKanban, color: "text-green-600" },
  { label: "剧情创意", value: "0", icon: FileText, color: "text-purple-600" },
  { label: "核心人物", value: "0", icon: Users, color: "text-orange-600" },
  { label: "广告成片", value: "0", icon: CheckCircle2, color: "text-blue-600" },
  { label: "合规审核", value: "0", icon: BarChart3, color: "text-red-600" },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">工作台</h1>
        <div className="text-sm text-gray-500">AI Story Commerce 生产概览</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">{stat.label}</CardTitle>
              <stat.icon className={["w-5 h-5", stat.color].join(" ")} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">快速操作</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-blue-50 cursor-pointer group">
              <div>
                <div className="text-sm font-medium text-gray-900">创建新项目</div>
                <div className="text-xs text-gray-500">开始新的商业广告项目</div>
              </div>
              <div className="w-8 h-8 rounded bg-blue-100 flex items-center justify-center text-blue-600 group-hover:bg-blue-200 transition-colors">
                <Plus className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-green-50 cursor-pointer group">
              <div>
                <div className="text-sm font-medium text-gray-900">新建商品资料</div>
                <div className="text-xs text-gray-500">添加待制作的商品</div>
              </div>
              <div className="w-8 h-8 rounded bg-green-100 flex items-center justify-center text-green-600 group-hover:bg-green-200 transition-colors">
                <Plus className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-purple-50 cursor-pointer group">
              <div>
                <div className="text-sm font-medium text-gray-900">生成剧情创意</div>
                <div className="text-xs text-gray-500">AI辅助创意生成</div>
              </div>
              <div className="w-8 h-8 rounded bg-purple-100 flex items-center justify-center text-purple-600 group-hover:bg-purple-200 transition-colors">
                <Plus className="w-4 h-4" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">最近活动</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-500">暂无活动记录</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">系统状态</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              <div className="text-sm text-gray-600">后端API正常</div>
            </div>
            <div className="mt-2 text-xs text-gray-400">数据库：SQLite | 环境：本地开发</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
