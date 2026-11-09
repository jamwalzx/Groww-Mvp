"use client";

export default function FallbackCard() {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 space-y-2">
      <p className="text-sm font-medium text-gray-700">
        I&apos;m not sure about this one.
      </p>
      <p className="text-sm text-gray-600">
        The official place to check is Groww Help:
      </p>
      <a
        href="https://groww.in/help"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block text-sm font-medium text-green-600 hover:text-green-700 underline"
      >
        https://groww.in/help →
      </a>
    </div>
  );
}

