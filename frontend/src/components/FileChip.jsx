import { X } from "lucide-react";

export default function FileChip({ file, onRemove }) {
  const isImage = file.type && file.type.startsWith("image/");
  const previewUrl = isImage ? URL.createObjectURL(file) : null;

  return (
    <div className="flex items-center gap-2 border border-[var(--foreground)] px-3 py-2 shrink-0">
      {previewUrl && (
        <img
          src={previewUrl}
          alt={file.name}
          className="w-10 h-10 object-cover border border-[var(--foreground)]"
        />
      )}
      <span
        className="text-xs max-w-[120px] truncate"
        style={{ fontFamily: '"JetBrains Mono", monospace' }}
      >
        {file.name}
      </span>
      <button
        onClick={() => onRemove(file)}
        className="ml-1 cursor-pointer bg-transparent border-none p-0 flex items-center text-[var(--foreground)] hover:text-[var(--muted-foreground)] transition-colors duration-100"
        aria-label={`Remove ${file.name}`}
      >
        <X size={14} strokeWidth={1.5} />
      </button>
    </div>
  );
}
