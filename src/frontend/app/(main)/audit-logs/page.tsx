"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Button, Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function AuditLogsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">操作审计</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>审计日志列表</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>操作</TableHead>
                  <TableHead>资源类型</TableHead>
                  <TableHead>资源ID</TableHead>
                  <TableHead>用户</TableHead>
                  <TableHead>操作时间</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-gray-500 py-4">
                    暂无审计日志
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
