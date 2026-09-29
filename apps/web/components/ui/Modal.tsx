'use client';

import React from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export default function Modal({ isOpen, onClose, title, children }: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-5">
      <div className="bg-[#1B1C1A] border border-hairline rounded-2xl max-w-[380px] w-full max-h-[80vh] overflow-y-auto p-6 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <h3 className="font-serif text-2xl text-amber mb-3">{title}</h3>
        <div className="text-sm text-muted leading-relaxed mb-5">{children}</div>
        <button
          onClick={onClose}
          className="w-full py-2.5 bg-amber hover:bg-amber-dark text-[#111210] font-semibold rounded-lg text-sm transition-colors cursor-pointer"
        >
          Done
        </button>
      </div>
    </div>
  );
}
