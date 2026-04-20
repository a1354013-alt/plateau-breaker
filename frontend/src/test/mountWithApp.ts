import { mount, type MountingOptions, type VueWrapper } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Tooltip from 'primevue/tooltip'
import type { Component } from 'vue'

type AnyProps = Record<string, unknown>

export function mountWithApp<T extends Component>(
  component: T,
  options: MountingOptions<AnyProps> = {},
): VueWrapper {
  const globalOptions = options.global ?? {}
  const existingPlugins = globalOptions.plugins ?? []

  const plugins = [
    ...existingPlugins,
    [
      PrimeVue,
      {
        theme: {
          preset: Aura,
          options: { darkModeSelector: '.dark-mode' },
        },
      },
    ],
    ToastService,
    ConfirmationService,
  ] as unknown as NonNullable<typeof globalOptions.plugins>

  return mount(component, {
    ...options,
    global: {
      ...globalOptions,
      plugins,
      directives: {
        tooltip: Tooltip,
        ...(globalOptions.directives ?? {}),
      },
      stubs: {
        RouterLink: true,
        Teleport: true,
        ...(globalOptions.stubs ?? {}),
      },
    },
  })
}
