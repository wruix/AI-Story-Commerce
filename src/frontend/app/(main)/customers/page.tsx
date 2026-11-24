"use client"

import { useState, useEffect } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Button, Input, Card, CardContent, CardHeader, CardTitle, Badge } from "@/components/ui/card"
import { Plus, Search, Edit, Trash2, FileText } from "lucide-react"
import { customerApi } from "@/lib/api"
import type { Customer } from "@/types"
import type { CustomerCreate } from "@/types/api"

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState<CustomerCreate>({
    name: "",
    contact_person: "",
    phone: "",
    email: "",
    company: "",
    address: "",
    notes: "",
  })

  useEffect(() => {
    loadCustomers()
  }, [])

  async function loadCustomers() {
    setLoading(true)
    try {
      const data = await customerApi.list()
      setCustomers(Array.isArray(data) ? data : [])
    } catch (e) {
      console.error("Failed to load customers", e)
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (editingId) {
        await customerApi.update(editingId, formData)
      } else {
        await customerApi.create(formData)
      }
      setShowForm(false)
      setEditingId(null)
      setFormData({ name: "", contact_person: "", phone: "", email: "", company: "", address: "", notes: "" })
      await loadCustomers()
    } catch (e) {
      alert("保存失败：" + (e as Error).message)
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm("确定要删除该客户吗？")) return
    try {
      await customerApi.delete(id)
      await loadCustomers()
    } catch (e) {
      alert("删除失败：" + (e as Error).message)
    }
  }

  function handleEdit(c: Customer) {
    setEditingId(c.id)
    setFormData({
      name: c.name,
      contact_person: c.contact_person || "",
      phone: c.phone || "",
      email: c.email || "",
      company: c.company || "",
      address: c.address || "",
      notes: c.notes || "",
    })
    setShowForm(true)
  }

  const filtered = customers.filter(
    (c) => c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (c.contact_person && c.contact_person.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">客户管理</h1>
          <p className="text-sm text-gray-500">管理商家客户资料，支持客户项目关联</p>
        </div>
        <Button variant="default" onClick={() => { setEditingId(null); setFormData({ name: "", contact_person: "", phone: "", email: "", company: "", address: "", notes: "" }); setShowForm(true) }}>
          <Plus size={18} /> 新建客户
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <CardTitle>客户列表</CardTitle>
            <Input placeholder="搜索客户名称/联系人..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-64" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>客户名称</TableHead>
                  <TableHead>联系人</TableHead>
                  <TableHead>电话</TableHead>
                  <TableHead>邮箱</TableHead>
                  <TableHead>公司</TableHead>
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-gray-500 py-4">
                      加载中...
                    </TableCell>
                  </TableRow>
                ) : filtered.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-gray-500 py-4">
                      暂无客户数据
                    </TableCell>
                  </TableRow>
                ) : (
                  filtered.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>{c.name}</TableCell>
                      <TableCell>{c.contact_person || "—"}</TableCell>
                      <TableCell>{c.phone || "—"}</TableCell>
                      <TableCell>{c.email || "—"}</TableCell>
                      <TableCell>{c.company || "—"}</TableCell>
                      <TableCell className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => handleEdit(c)}>
                          <Edit size={14} /> 编辑
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleDelete(c.id)}>
                          <Trash2 size={14} /> 删除
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>{editingId ? "编辑客户" : "新建客户"}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <Input label="客户名称 *" placeholder="输入客户名称" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value || ""})} />
              </div>
              <div>
                <Input label="联系人" placeholder="联系人姓名" value={formData.contact_person || ""} onChange={(e) => setFormData({...formData, contact_person: e.target.value || ""})} />
              </div>
              <div>
                <Input label="电话" placeholder="联系电话" value={formData.phone || ""} onChange={(e) => setFormData({...formData, phone: e.target.value || ""})} />
              </div>
              <div>
                <Input label="邮箱" type="email" placeholder="联系邮箱" value={formData.email || ""} onChange={(e) => setFormData({...formData, email: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2">
                <Input label="公司名称" placeholder="所在公司" value={formData.company || ""} onChange={(e) => setFormData({...formData, company: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2">
                <Input label="地址" placeholder="公司地址" value={formData.address || ""} onChange={(e) => setFormData({...formData, address: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2">
                <TextareaAuto label="备注" placeholder="客户备注信息" value={formData.notes || ""} onChange={(e) => setFormData({...formData, notes: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2 flex items-end gap-2">
                <Button type="button" variant="outline" onClick={() => { setShowForm(false); setEditingId(null) }}>取消</Button>
                <Button type="submit">保存客户</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function TextareaAuto({ label, value, onChange, placeholder }: { label?: string; value: string; onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void; placeholder?: string }) {
  return (
    <div className="space-y-1">
      {label && <label className="text-sm font-medium text-gray-700">{label}</label>}
      <textarea
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        rows={3}
      />
    </div>
  )
}
