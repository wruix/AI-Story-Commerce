"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Button, Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function PerformanceMetricsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">数据分析</h1>
        <Button variant="default">录入效果数据</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>广告效果数据</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>发布记录</TableHead>
                  <TableHead>播放量</TableHead>
                  <TableHead>完播率</TableHead>
                  <TableHead>点击</TableHead>
                  <TableHead>订单</TableHead>
                  <TableHead>成本(CNY)</TableHead>
                  <TableHead>ROAS</TableHead>
                  <TableHead>记录时间</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-gray-500 py-4">
                    暂无效果数据
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
