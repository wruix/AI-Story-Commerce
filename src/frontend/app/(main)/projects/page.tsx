"use client"

import { useState } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Button, Input, Card, CardContent, CardHeader, CardTitle, Badge } from "@/components/ui/card"
import { Search } from "lucide-react"

export default function ProjectsPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [projects, setProjects] = useState<any[]>([])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">项目列表</h1>
        <Button variant="default">新建项目</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>项目列表</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>项目名称</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>预算 (CNY)</TableHead>
                  <TableHead>客户</TableHead>
                  <TableHead>创建时间</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projects.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-gray-500 py-4">
                      暂无项目数据
                    </TableCell>
                  </TableRow>
                ) : (
                  projects.map((p) => (
                    <TableRow key={p.id}>
                      <TableCell>{p.name}</TableCell>
                      <TableCell>
                        <Badge variant="default">{p.status}</Badge>
                      </TableCell>
                      <TableCell>{p.budget_cny || "—"}</TableCell>
                      <TableCell>{p.customer_id || "—"}</TableCell>
                      <TableCell>{new Date(p.created_at).toLocaleDateString("zh-CN")}</TableCell>
                      <TableCell>
                        <Button size="sm" variant="outline">查看</Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
