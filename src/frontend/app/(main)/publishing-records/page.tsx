"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Button, Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function PublishingRecordsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">发布记录</h1>
        <Button variant="default">新建发布记录</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>发布记录列表</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>广告ID</TableHead>
                  <TableHead>平台</TableHead>
                  <TableHead>账号</TableHead>
                  <TableHead>发布时间</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-gray-500 py-4">
                    暂无发布记录
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
