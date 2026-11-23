"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Button, Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function StoryboardsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">分镜管理</h1>
        <Button variant="default">新建分镜</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>分镜列表</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>镜头号</TableHead>
                  <TableHead>剧本</TableHead>
                  <TableHead>画面提示词</TableHead>
                  <TableHead>时长(秒)</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-gray-500 py-4">
                    暂无分镜数据
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
