"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Button, Card, CardContent, CardHeader, CardTitle, Badge } from "@/components/ui/card"

export default function ProductsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">商品库</h1>
        <Button variant="default">新建商品</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>商品列表</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>商品名称</TableHead>
                  <TableHead>类别</TableHead>
                  <TableHead>价格 (CNY)</TableHead>
                  <TableHead>项目</TableHead>
                  <TableHead>创建时间</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-gray-500 py-4">
                    暂无商品数据
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
