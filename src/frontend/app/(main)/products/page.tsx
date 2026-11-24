"use client"

import { useState, useEffect } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Button, Input, Card, CardContent, CardHeader, CardTitle, Badge, Select } from "@/components/ui/card"
import { Plus, Search, Edit, Trash2, Image as ImageIcon, FileText } from "lucide-react"
import { productApi } from "@/lib/api"
import type { Product } from "@/types"
import type { ProductCreate } from "@/types/api"

const CATEGORIES = [
  { value: "home_cleaning", label: "家居清洁" },
  { value: "daily_goods", label: "日用百货" },
  { value: "apparel_warmth", label: "服装保暖" },
  { value: "other", label: "其他" },
]

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState<ProductCreate>({
    project_id: "",
    name: "",
    category: "other",
    price_cny: undefined,
    specifications: "",
    selling_points: "",
    target_audience: "",
    usage_scenarios: "",
    proof_materials: "",
    image_url: "",
  })

  useEffect(() => {
    loadProducts()
  }, [])

  async function loadProducts() {
    setLoading(true)
    try {
      const data = await productApi.list()
      setProducts(Array.isArray(data) ? data : [])
    } catch (e) {
      console.error("Failed to load products", e)
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (editingId) {
        await productApi.update(editingId, formData)
      } else {
        await productApi.create(formData)
      }
      setShowForm(false)
      setEditingId(null)
      setFormData({
        project_id: "",
        name: "",
        category: "other",
        price_cny: undefined,
        specifications: "",
        selling_points: "",
        target_audience: "",
        usage_scenarios: "",
        proof_materials: "",
        image_url: "",
      })
      await loadProducts()
    } catch (e) {
      alert("保存失败：" + (e as Error).message)
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm("确定要删除该商品吗？")) return
    try {
      await productApi.delete(id)
      await loadProducts()
    } catch (e) {
      alert("删除失败：" + (e as Error).message)
    }
  }

  function handleEdit(p: Product) {
    setEditingId(p.id)
    setFormData({
      project_id: p.project_id,
      name: p.name,
      category: p.category,
      price_cny: p.price_cny,
      specifications: p.specifications || "",
      selling_points: p.selling_points || "",
      target_audience: p.target_audience || "",
      usage_scenarios: p.usage_scenarios || "",
      proof_materials: p.proof_materials || "",
      image_url: p.image_url || "",
    })
    setShowForm(true)
  }

  const filtered = products.filter(
    (p) => p.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">商品库</h1>
          <p className="text-sm text-gray-500">管理所有商品资料，支持AI编剧引擎的商品分析</p>
        </div>
        <Button variant="default" onClick={() => { setEditingId(null); setFormData({ project_id: "", name: "", category: "other", price_cny: undefined, specifications: "", selling_points: "", target_audience: "", usage_scenarios: "", proof_materials: "", image_url: "" }); setShowForm(true) }}>
          <Plus size={18} /> 新建商品
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <CardTitle>商品列表</CardTitle>
            <Input placeholder="搜索商品名称..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-64" />
          </div>
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
                  <TableHead>操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-gray-500 py-4">
                      加载中...
                    </TableCell>
                  </TableRow>
                ) : filtered.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-gray-500 py-4">
                      暂无商品数据
                    </TableCell>
                  </TableRow>
                ) : (
                  filtered.map((p) => (
                    <TableRow key={p.id}>
                      <TableCell>{p.name}</TableCell>
                      <TableCell>
                        <Badge variant="default">{CATEGORIES.find(c => c.value === p.category)?.label || p.category}</Badge>
                      </TableCell>
                      <TableCell>{p.price_cny !== undefined ? p.price_cny.toFixed(2) : "—"}</TableCell>
                      <TableCell>{p.project_id || "—"}</TableCell>
                      <TableCell className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => handleEdit(p)}>
                          <Edit size={14} /> 编辑
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleDelete(p.id)}>
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
            <CardTitle>{editingId ? "编辑商品" : "新建商品"}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <Input label="项目 ID" placeholder="关联的项目ID" value={formData.project_id} onChange={(e) => setFormData({...formData, project_id: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2">
                <Input label="商品名称 *" placeholder="输入商品名称" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value || ""})} />
              </div>
              <div>
                <Select label="商品类别" value={formData.category} onChange={(val) => setFormData({...formData, category: val as any})} options={CATEGORIES} />
              </div>
              <div>
                <Input label="价格 (CNY)" type="number" value={formData.price_cny ?? ""} onChange={(e) => setFormData({...formData, price_cny: e.target.value ? parseFloat(e.target.value) : undefined})} />
              </div>
              <div className="md:col-span-2">
                <Input label="规格参数" placeholder="商品规格详情" value={formData.specifications || ""} onChange={(e) => setFormData({...formData, specifications: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2">
                <TextareaAuto label="商品卖点" placeholder="商品核心卖点，供AI编剧引擎分析" value={formData.selling_points || ""} onChange={(e) => setFormData({...formData, selling_points: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2">
                <TextareaAuto label="目标人群" placeholder="适用人群描述" value={formData.target_audience || ""} onChange={(e) => setFormData({...formData, target_audience: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2">
                <TextareaAuto label="使用场景" placeholder="商品使用场景" value={formData.usage_scenarios || ""} onChange={(e) => setFormData({...formData, usage_scenarios: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2">
                <TextareaAuto label="真实证明材料" placeholder="功效证明、检测报告等合规材料" value={formData.proof_materials || ""} onChange={(e) => setFormData({...formData, proof_materials: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2">
                <Input label="商品图片 URL" placeholder="商品图片地址" value={formData.image_url || ""} onChange={(e) => setFormData({...formData, image_url: e.target.value || ""})} />
              </div>
              <div className="md:col-span-2 flex items-end gap-2">
                <Button type="button" variant="outline" onClick={() => { setShowForm(false); setEditingId(null) }}>取消</Button>
                <Button type="submit">保存商品</Button>
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
