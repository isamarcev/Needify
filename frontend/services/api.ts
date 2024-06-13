const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

// Users
export async function getUsers() {
  const res = await fetch(`${BASE_URL}/v1/users/list`, { mode: 'no-cors' });

  if (!res.ok) {
    throw new Error('Failed to get users');
  }

  return res.json();
}

// Currency

// Task
export async function getTasks() {
  const res = await fetch(`${BASE_URL}/v1/task`, { mode: 'no-cors' });

  if (!res.ok) {
    throw new Error('Failed to get users');
  }

  return res.json();
}

// Job-offer

// Category

// Ton-connect
