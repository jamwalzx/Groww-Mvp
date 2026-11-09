"use client";

import Link from "next/link";

export default function NavBar() {
  return (
    <nav className="flex items-center justify-between mb-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">
          Plan B for my SIP
        </h1>
        <p className="text-sm text-gray-500 mt-0.5">
          For first-time SIP investors on Groww
        </p>
      </div>
      <Link
        href="/eval"
        className="text-sm text-gray-500 hover:text-gray-700 underline underline-offset-2"
      >
        Eval Suite →
      </Link>
    </nav>
  );
}

