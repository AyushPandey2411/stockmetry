// src/pages/Products.tsx
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { LoadingState, ErrorState, DataTable, TR, TD } from '../components/ui'
import { Package } from 'lucide-react'

export default function ProductsPage() {
  const { data: products, isLoading, error } = useQuery({
    queryKey: ['products'],
    queryFn: () => api.get('/products/').then(r => r.data),
  })

  if (isLoading) return <LoadingState label="Loading products..." />
  if (error)     return <ErrorState message="Failed to load products" />

  return (
    <div className="space-y-5 page-enter">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif font-bold text-lg">{products.length} Products</h2>
          <p className="text-xs text-white/40 font-mono mt-0.5">Active inventory catalog</p>
        </div>
      </div>

      <div className="card">
        <DataTable headers={['SKU','Name','Category','Price','Cost','Stock','Lead Time','Supplier','Zone']}>
          {products.map((p: any) => (
            <TR key={p.id}>
              <TD mono className="text-amber-light">{p.sku}</TD>
              <TD><span className="font-semibold">{p.name}</span></TD>
              <TD mono className="text-white/50">{p.category}</TD>
              <TD mono>${p.price}</TD>
              <TD mono className="text-white/50">${p.cost}</TD>
              <TD mono className={p.current_stock === 0 ? 'text-rose-light font-bold' : 'text-jade-light'}>{p.current_stock}</TD>
              <TD mono className="text-white/50">{p.lead_time_days}d</TD>
              <TD className="text-white/50 text-xs">{p.supplier || '—'}</TD>
              <TD mono className="text-violet-light">{p.warehouse_zone}</TD>
            </TR>
          ))}
        </DataTable>
      </div>
    </div>
  )
}
