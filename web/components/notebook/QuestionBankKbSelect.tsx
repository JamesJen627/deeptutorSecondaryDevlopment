"use client";

import { BookOpen } from "lucide-react";
import { useTranslation } from "react-i18next";
import {
  QUESTION_BANK_UNTAGGED_KB,
  type NotebookKbStats,
} from "@/lib/notebook-api";

export type QuestionBankKbOption = NotebookKbStats["items"][number];

type QuestionBankKbSelectProps = {
  value: string | null;
  onChange: (kbName: string | null) => void;
  options: QuestionBankKbOption[];
  untaggedCount?: number;
  totalCount?: number;
  disabled?: boolean;
};

export default function QuestionBankKbSelect({
  value,
  onChange,
  options,
  untaggedCount = 0,
  totalCount,
  disabled = false,
}: QuestionBankKbSelectProps) {
  const { t } = useTranslation();
  const hasChoices = options.length > 0 || untaggedCount > 0;
  if (!hasChoices) {
    return null;
  }

  const formatCount = (count: number) =>
    totalCount !== undefined ? ` (${count})` : "";

  return (
    <label className="inline-flex items-center gap-1.5">
      <BookOpen className="h-3.5 w-3.5 shrink-0 text-[var(--muted-foreground)]" />
      <select
        value={value ?? ""}
        onChange={(e) => {
          const next = e.target.value;
          if (!next) {
            onChange(null);
            return;
          }
          onChange(next);
        }}
        disabled={disabled}
        aria-label={t("Knowledge Base")}
        className="max-w-[240px] truncate rounded-lg border border-[var(--border)] bg-[var(--background)] px-2.5 py-1.5 text-[12px] text-[var(--foreground)] outline-none transition-colors hover:bg-[var(--muted)]/40 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <option value="">
          {t("All knowledge bases")}
          {totalCount !== undefined ? ` (${totalCount})` : ""}
        </option>
        {untaggedCount > 0 ? (
          <option value={QUESTION_BANK_UNTAGGED_KB}>
            {t("Untagged knowledge base")}
            {formatCount(untaggedCount)}
          </option>
        ) : null}
        {options.map(({ kb_name, count }) => (
          <option key={kb_name} value={kb_name}>
            {kb_name}
            {formatCount(count)}
          </option>
        ))}
      </select>
    </label>
  );
}
