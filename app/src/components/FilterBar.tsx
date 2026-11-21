import { FILTERS, type Filter } from '../state'

export default function FilterBar({
  filter,
  onFilter,
}: {
  filter: Filter
  onFilter: (f: Filter) => void
}) {
  return (
    <div className="filterbar">
      <div className="filter-pills">
        {FILTERS.map(f => (
          <button
            key={f.id}
            className={filter === f.id ? 'filter-pill on' : 'filter-pill'}
            onClick={() => onFilter(f.id)}
          >
            {f.label}
          </button>
        ))}
        <button className="filter-add" title="Tambah filter" aria-label="Tambah filter">
          +
        </button>
      </div>
      <div className="quick-actions">
        <button className="quick-btn" title="Muat ulang" aria-label="Muat ulang">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 11a8 8 0 1 0-2.3 5.7" />
            <path d="M20 5v6h-6" />
          </svg>
        </button>
        <button className="quick-btn" title="Favorit" aria-label="Favorit">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 3l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8L3.5 9.2l5.9-.9L12 3Z" />
          </svg>
        </button>
      </div>
    </div>
  )
}
