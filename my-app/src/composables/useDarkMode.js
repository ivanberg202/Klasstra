import { ref, onMounted } from 'vue';

export function useDarkMode() {
  const isDarkMode = ref(false);

  function initDarkMode() {
    const savedTheme = localStorage.getItem('theme');
    isDarkMode.value =
      savedTheme === 'dark' ||
      (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches);

    if (isDarkMode.value) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  function toggleDarkMode(event) {
    isDarkMode.value = !isDarkMode.value;
    document.documentElement.classList.toggle('dark', isDarkMode.value);
    localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light');
    if (event) event.target.blur();
  }

  onMounted(initDarkMode);

  return { isDarkMode, toggleDarkMode };
}
