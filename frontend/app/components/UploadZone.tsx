"use client";

import { useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, Loader2, CheckCircle2, AlertCircle, X } from "lucide-react";
import { cn } from "@/lib/utils";

export type UploadState = "idle" | "dragging" | "uploading" | "processing" | "analyzing" | "done" | "error";

interface UploadZoneProps {
  state: UploadState;
  fileName: string | null;
  errorMessage: string | null;
  onFileSelected: (file: File) => void;
  onClear: () => void;
}

const STATE_LABEL: Record<UploadState, string> = {
  idle: "Drop your resume here",
  dragging: "Release to upload",
  uploading: "Uploading file…",
  processing: "Extracting text…",
  analyzing: "Running diagnostic…",
  done: "Ready",
  error: "Something went wrong",
};

export function UploadZone({ state, fileName, errorMessage, onFileSelected, onClear }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files?.[0];
      if (file) onFileSelected(file);
    },
    [onFileSelected]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onFileSelected(file);
    },
    [onFileSelected]
  );

  const isBusy = state === "uploading" || state === "processing" || state === "analyzing";
  const isDone = state === "done";
  const isError = state === "error";

  return (
    <div className="w-full">
      <motion.div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !isBusy && !isDone && inputRef.current?.click()}
        className={cn(
          "relative rounded-2xl border-2 border-dashed px-8 py-14 text-center transition-colors cursor-pointer",
          "flex flex-col items-center justify-center gap-3",
          isDragOver && "border-signal bg-signal/5",
          !isDragOver && !isError && "border-ink-600/30 bg-paper-100/60 hover:border-ink-600/50",
          isError && "border-verdict-bad/50 bg-verdict-bad/5",
          isDone && "border-verdict-good/50 bg-verdict-good/5 cursor-default",
          isBusy && "cursor-wait"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.doc"
          className="hidden"
          onChange={handleFileInput}
          disabled={isBusy}
        />

        <AnimatePresence mode="wait">
          {isBusy && (
            <motion.div
              key="busy"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-3"
            >
              <Loader2 className="w-9 h-9 text-signal animate-spin" />
              <p className="font-medium text-ink-900">{STATE_LABEL[state]}</p>
              <div className="flex gap-1.5 mt-1">
                {(["uploading", "processing", "analyzing"] as UploadState[]).map((s) => (
                  <div
                    key={s}
                    className={cn(
                      "h-1 w-8 rounded-full transition-colors",
                      ["uploading", "processing", "analyzing"].indexOf(state) >=
                        ["uploading", "processing", "analyzing"].indexOf(s)
                        ? "bg-signal"
                        : "bg-ink-600/15"
                    )}
                  />
                ))}
              </div>
            </motion.div>
          )}

          {isDone && fileName && (
            <motion.div
              key="done"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center gap-2"
            >
              <CheckCircle2 className="w-9 h-9 text-verdict-good" />
              <p className="font-medium text-ink-900 flex items-center gap-2">
                <FileText className="w-4 h-4" /> {fileName}
              </p>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onClear();
                }}
                className="mt-1 text-xs text-ink-600 hover:text-ink-900 flex items-center gap-1 underline"
              >
                <X className="w-3 h-3" /> Replace file
              </button>
            </motion.div>
          )}

          {isError && (
            <motion.div
              key="error"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center gap-2"
            >
              <AlertCircle className="w-9 h-9 text-verdict-bad" />
              <p className="font-medium text-verdict-bad">{errorMessage || "Upload failed"}</p>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onClear();
                }}
                className="mt-1 text-xs text-ink-600 hover:text-ink-900 underline"
              >
                Try again
              </button>
            </motion.div>
          )}

          {state === "idle" && (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center gap-3"
            >
              <div className="rounded-full bg-ink-950 p-3.5">
                <Upload className="w-5 h-5 text-paper-50" />
              </div>
              <div>
                <p className="font-medium text-ink-900">Drop your resume here</p>
                <p className="text-sm text-ink-600 mt-1">PDF or DOCX, up to 10MB · click to browse</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
