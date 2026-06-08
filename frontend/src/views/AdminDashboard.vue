<template>
  <div>
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" location="top">
      {{ snackbar.text }}
    </v-snackbar>
    <v-app-bar color="primary" density="compact" class="px-4 py-2 app-dashboard-bar">
      <AppHeaderLogo :height-px="32" href="/" class="app-dashboard-bar__logo" />
      <v-app-bar-title class="pl-2">Панель администратора</v-app-bar-title>
      <v-spacer />
      <span class="mr-2">{{ userStore.user?.username }}</span>
      <v-btn variant="text" icon="mdi-logout" @click="logout" />
    </v-app-bar>

    <v-main class="pa-50 bg-surface-variant">
      <v-container fluid class="pa-0 pa-sm-4">
        <v-tabs v-model="activeTab" class="mb-4 vuvoz-tabs" color="primary" show-arrows>
          <v-tab value="prices">Материалы</v-tab>
          <v-tab value="news">Новости</v-tab>
          <v-tab value="companies">Компании</v-tab>
          <v-tab value="institutions">Организации</v-tab>
          <v-tab value="registration-institutions">Регистрация: учреждения</v-tab>
          <v-tab value="registration-companies">Регистрация: компании</v-tab>
          <v-tab value="pickup-requests">Заявки на вывоз</v-tab>
          <v-tab value="requests">Заявки</v-tab>
          <v-tab value="statistics">Статистика</v-tab>
          <v-tab value="bonuses">Бонусы</v-tab>
          <v-tab value="support">Техподдержка</v-tab>
          <v-tab value="products">Товары (баллы)</v-tab>
          <v-tab value="points-orders">Заказы на баллы</v-tab>
          <v-tab value="audit-logs">Логи действий</v-tab>
          <v-tab value="database-info">База данных</v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <!-- Materials (prices) -->
          <v-window-item value="prices">
            <v-card class="rounded-lg vuvoz-content-card" elevation="1">
              <v-card-title class="d-flex flex-wrap align-center ga-2">
                <span class="text-h6">Управление материалами</span>
                <v-spacer />
                <v-text-field
                  v-model="materialSearch"
                  placeholder="Поиск по названию"
                  density="compact"
                  hide-details
                  clearable
                  class="admin-materials-search"
                  style="max-width: 220px;"
                />
                <v-btn variant="outlined" prepend-icon="mdi-tag-plus" @click="openMaterialDialog()">
                  Добавить тип материала
                </v-btn>
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openPriceDialog()">
                  Добавить цену
                </v-btn>
              </v-card-title>
              <v-divider />
              <div class="overflow-x-auto">
                <v-data-table
                  :headers="priceHeaders"
                  :items="filteredPrices"
                  :loading="loadingPrices"
                  item-value="id"
                  class="admin-materials-table"
                  :mobile-breakpoint="600"
                >
                  <template #item.material_name="{ item }">
                    {{ item.material_name || item.material_code }}
                  </template>
                  <template #item.price_per_kg="{ item }">
                    {{ item.price_per_kg }} руб/кг
                  </template>
                  <template #item.is_active="{ item }">
                    <v-chip :color="item.is_active ? 'success' : 'grey'" size="small" variant="tonal">
                      {{ item.is_active ? 'Активен' : 'Неактивен' }}
                    </v-chip>
                  </template>
                  <template #item.actions="{ item }">
                    <div class="d-flex flex-wrap ga-1">
                      <v-btn size="small" variant="text" density="comfortable" @click="openPriceDialog(item)">
                        Изменить
                      </v-btn>
                      <v-btn
                        size="small"
                        variant="text"
                        :color="item.is_active ? 'warning' : 'success'"
                        density="comfortable"
                        @click="togglePriceActive(item)"
                      >
                        {{ item.is_active ? 'Деактивировать' : 'Активировать' }}
                      </v-btn>
                    </div>
                  </template>
                </v-data-table>
              </div>
              <v-alert v-if="priceFormError" type="error" density="compact" class="ma-3" closable @click:close="priceFormError = ''">
                {{ priceFormError }}
              </v-alert>
            </v-card>

            <v-card class="rounded-lg vuvoz-content-card mt-4" elevation="1">
              <v-card-title class="text-h6">Типы материалов</v-card-title>
              <v-card-subtitle class="pb-0">
                Фото — для главной и каталога сырья. Иконка — для калькулятора (96×96), если фото нет.
              </v-card-subtitle>
              <v-divider class="mt-2" />
              <div class="overflow-x-auto">
                <v-data-table
                  :headers="materialHeaders"
                  :items="filteredMaterialCatalog"
                  :loading="loadingMaterials"
                  item-value="id"
                  class="admin-materials-table"
                  :mobile-breakpoint="600"
                >
                  <template #item.icon_url="{ item }">
                    <v-img
                      v-if="resolveMediaUrl(item.icon_url)"
                      :src="resolveMediaUrl(item.icon_url)"
                      width="40"
                      height="40"
                      class="rounded admin-material-thumb"
                      cover
                    />
                    <v-icon v-else :icon="materialMdiIcon(item.code, item.icon)" size="28" color="primary" />
                  </template>
                  <template #item.image_url="{ item }">
                    <v-img
                      v-if="resolveMediaUrl(item.image_url)"
                      :src="resolveMediaUrl(item.image_url)"
                      width="56"
                      height="40"
                      class="rounded admin-material-thumb"
                      cover
                    />
                    <span v-else class="text-medium-emphasis">—</span>
                  </template>
                  <template #item.is_active="{ item }">
                    <v-chip :color="item.is_active ? 'success' : 'grey'" size="small" variant="tonal">
                      {{ item.is_active ? 'Активен' : 'Неактивен' }}
                    </v-chip>
                  </template>
                  <template #item.actions="{ item }">
                    <v-btn size="small" variant="text" @click="openMaterialDialog(item)">Изменить</v-btn>
                  </template>
                </v-data-table>
              </div>
            </v-card>

<v-dialog
              v-model="priceDialog"
              :fullscreen="fullscreenModal"
              max-width="500"
              persistent
              scrollable
              class="admin-dialog"
            >
              <v-card>
                <v-card-title>{{ editingPrice ? 'Редактировать цену' : 'Добавить цену' }}</v-card-title>
                <v-card-text>
                  <v-select
                    v-model="priceForm.material"
                    :items="availableMaterialsForPrice"
                    item-title="name"
                    item-value="id"
                    label="Материал *"
                    variant="outlined"
                    class="mb-3"
                    :disabled="!!editingPrice"
                    :no-data-text="editingPrice ? '' : 'Нет материалов без цены. Сначала добавьте тип материала.'"
                  />
                  <v-text-field
                    v-model.number="priceForm.price_per_kg"
                    label="Цена за кг (руб) *"
                    type="number"
                    min="0"
                    step="0.01"
                    variant="outlined"
                    class="mb-3"
                    :error-messages="priceFormErrors.price_per_kg"
                  />
                  <v-switch v-model="priceForm.is_active" label="Активен (отображается в заявках)" color="primary" hide-details class="mb-2" />
                </v-card-text>
                <v-card-actions class="px-4 pb-4">
                  <v-spacer />
                  <v-btn variant="text" @click="priceDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingPrice" @click="savePrice">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog
              v-model="materialDialog"
              :fullscreen="fullscreenModal"
              max-width="560"
              persistent
              scrollable
              class="admin-dialog"
            >
              <v-card>
                <v-card-title>{{ editingMaterial ? 'Редактировать тип материала' : 'Новый тип материала' }}</v-card-title>
                <v-card-text>
                  <v-text-field
                    v-model="materialForm.name"
                    label="Название *"
                    variant="outlined"
                    class="mb-3"
                    :error-messages="materialFormErrors.name"
                  />
                  <v-text-field
                    v-model="materialForm.code"
                    label="Код (латиница, например cardboard) *"
                    variant="outlined"
                    class="mb-3"
                    :error-messages="materialFormErrors.code"
                    :disabled="!!editingMaterial"
                  />
                  <v-textarea
                    v-model="materialForm.short_description"
                    label="Краткое описание (каталог)"
                    variant="outlined"
                    class="mb-3"
                    rows="2"
                  />
                  <v-text-field
                    v-model.number="materialForm.sort_order"
                    label="Порядок на главной"
                    type="number"
                    min="0"
                    variant="outlined"
                    class="mb-3"
                  />

                  <p class="text-subtitle-2 mb-2">Иконка (главная, калькулятор)</p>
                  <p class="text-caption text-medium-emphasis mb-2">
                    Загружается как квадрат 96×96 px. Если иконки нет — используется запасная MDI-иконка.
                  </p>
                  <div class="d-flex flex-wrap ga-4 mb-3 align-start">
                    <div class="admin-material-preview-box admin-material-preview-box--icon">
                      <img
                        v-if="materialForm.iconPreview"
                        :src="materialForm.iconPreview"
                        alt="Превью иконки"
                        class="admin-material-preview-box__img"
                      />
                      <v-icon v-else :icon="materialMdiIcon(materialForm.code, materialForm.icon)" size="40" color="primary" />
                    </div>
                    <div class="flex-grow-1" style="min-width: 200px;">
                      <v-file-input
                        v-model="materialForm.iconImageFile"
                        label="Загрузить иконку"
                        variant="outlined"
                        accept="image/*"
                        prepend-inner-icon="mdi-star-circle"
                        clearable
                        show-size
                        hide-details
                        @click:clear="onClearMaterialIcon"
                      />
                      <v-text-field
                        v-model="materialForm.icon"
                        label="Запасная MDI-иконка (package-variant)"
                        variant="outlined"
                        class="mt-3"
                        hide-details
                        density="compact"
                      />
                    </div>
                  </div>

                  <p class="text-subtitle-2 mb-2">Фото (главная и каталог «Сырьё и цены»)</p>
                  <div class="d-flex flex-wrap ga-4 mb-3 align-start">
                    <div class="admin-material-preview-box admin-material-preview-box--photo">
                      <img
                        v-if="materialForm.imagePreview"
                        :src="materialForm.imagePreview"
                        alt="Превью фото"
                        class="admin-material-preview-box__img"
                      />
                      <span v-else class="text-caption text-medium-emphasis">Нет фото</span>
                    </div>
                    <div class="flex-grow-1" style="min-width: 200px;">
                      <v-file-input
                        v-model="materialForm.imageFile"
                        label="Загрузить фото материала"
                        variant="outlined"
                        accept="image/*"
                        prepend-inner-icon="mdi-camera"
                        clearable
                        show-size
                        hide-details
                        @click:clear="onClearMaterialPhoto"
                      />
                    </div>
                  </div>

                  <v-switch v-model="materialForm.is_active" label="Активен" color="primary" hide-details />
                </v-card-text>
                <v-card-actions class="px-4 pb-4">
                  <v-spacer />
                  <v-btn variant="text" @click="materialDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingMaterial" @click="saveMaterial">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- News -->
          <v-window-item value="news">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Новости
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openNewsDialog()">
                  Добавить новость
                </v-btn>
              </v-card-title>
              <v-divider />
              <div class="overflow-x-auto">
              <v-data-table
                :headers="newsHeaders"
                :items="newsArticles"
                :loading="loadingNews"
                item-value="id"
                :mobile-breakpoint="600"
              >
                <template #item.is_published="{ item }">
                  <v-switch
                    :model-value="item.is_published"
                    hide-details
                    density="compact"
                    color="success"
                    @update:model-value="toggleNewsPublish(item)"
                  />
                </template>
                <template #item.created_at="{ item }">
                  {{ formatNewsDate(item.created_at) }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openNewsDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteNews(item)">Удалить</v-btn>
                </template>
              </v-data-table>
              </div>
            </v-card>

            <v-dialog
              v-model="newsDialog"
              :fullscreen="fullscreenModal"
              max-width="640"
              persistent
              scrollable
            >
              <v-card>
                <v-card-title>{{ editingNews ? 'Редактировать новость' : 'Новая новость' }}</v-card-title>
                <v-card-text style="max-height: 70vh" class="overflow-y-auto">
                  <v-text-field
                    v-model="newsForm.title"
                    label="Заголовок *"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-textarea
                    v-model="newsForm.content"
                    label="Содержание *"
                    variant="outlined"
                    rows="6"
                    class="mb-3"
                  />
                  <v-file-input
                    v-model="newsForm.imageFile"
                    label="Изображение (необяз.)"
                    accept="image/*"
                    prepend-icon=""
                    prepend-inner-icon="mdi-camera"
                    variant="outlined"
                    class="mb-3"
                    @update:model-value="onNewsImageChange"
                  />
                  <v-img
                    v-if="newsForm.imagePreview"
                    :src="newsForm.imagePreview"
                    max-height="200"
                    cover
                    class="rounded mb-3"
                  />
                  <v-checkbox v-model="newsForm.is_published" label="Опубликовано" />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="newsDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingNews" @click="saveNews">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog
              v-model="deleteNewsDialog"
              :fullscreen="fullscreenModal"
              max-width="400"
              persistent
            >
              <v-card>
                <v-card-title>Удалить новость?</v-card-title>
                <v-card-text>
                  Будет удалена новость «{{ newsToDelete?.title }}». Действие нельзя отменить.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteNewsDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingNews" @click="doDeleteNews">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Companies -->
          <v-window-item value="companies">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Все компании
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openCompanyDialog()">
                  Добавить компанию
                </v-btn>
              </v-card-title>
              <v-divider />
              <div class="overflow-x-auto">
              <v-data-table
                :headers="companyHeaders"
                :items="companies"
                :loading="loadingCompanies"
                item-value="id"
                :mobile-breakpoint="600"
              >
                <template #item.contact_phone="{ item }">
                  {{ item.contact_phone }} / {{ item.contact_email }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openCompanyCard(item)">Просмотр</v-btn>
                  <v-btn size="small" variant="text" @click="openCompanyDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteCompany(item)">Удалить</v-btn>
                </template>
              </v-data-table>
              </div>
            </v-card>

            <v-dialog
              v-model="companyCardDialog"
              :fullscreen="fullscreenModal"
              max-width="640"
              persistent
            >
              <v-card v-if="companyCard">
                <v-card-title class="d-flex align-center">
                  Карточка компании
                  <v-spacer />
                  <v-btn icon variant="text" @click="companyCardDialog = false">×</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="text-body-2">
                  <p><strong>Название:</strong> {{ companyCard.company_name }}</p>
                  <p><strong>Почта:</strong> {{ companyCard.contact_email }}</p>
                  <p><strong>Телефон:</strong> {{ companyCard.contact_phone }}</p>
                  <p><strong>Адрес:</strong> {{ companyCard.address || '—' }}</p>
                  <p><strong>Юр. адрес:</strong> {{ companyCard.legal_address || '—' }}</p>
                  <p><strong>ИНН:</strong> {{ companyCard.inn || '—' }}</p>
                  <p><strong>КПП:</strong> {{ companyCard.kpp || '—' }}</p>
                  <p><strong>ОГРН:</strong> {{ companyCard.ogrn || '—' }}</p>
                  <p><strong>Р/с:</strong> {{ companyCard.bank_account || '—' }}</p>
                  <p><strong>Банк:</strong> {{ companyCard.bank_name || '—' }}</p>
                  <p><strong>БИК:</strong> {{ companyCard.bik || '—' }}</p>
                  <p><strong>Корр. счёт:</strong> {{ companyCard.corr_account || '—' }}</p>
                  <p><strong>Сайт:</strong> {{ companyCard.website || '—' }}</p>
                  <p v-if="companyCard.description"><strong>Описание:</strong><br />{{ companyCard.description }}</p>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn color="primary" @click="companyCardDialog = false; openCompanyDialog(companyCard)">Изменить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog
              v-model="companyDialog"
              :fullscreen="fullscreenModal"
              max-width="600"
              persistent
              scrollable
            >
              <v-card>
                <v-card-title>{{ editingCompany ? 'Редактировать компанию' : 'Новая компания' }}</v-card-title>
                <v-card-text style="max-height: 70vh" class="overflow-y-auto">
                  <v-alert v-if="Object.keys(companyFormErrors).length" type="error" density="compact" class="mb-2">
                    <div v-for="(msgs, key) in companyFormErrors" :key="key">
                      {{ Array.isArray(msgs) ? msgs.join(' ') : msgs }}
                    </div>
                  </v-alert>
                  <v-text-field
                    v-model="companyForm.company_name"
                    label="Название компании *"
                    variant="outlined"
                    class="mb-2"
                    :error-messages="companyFormErrors.company_name"
                  />
                  <v-text-field
                    v-model="companyForm.contact_email"
                    label="Почта *"
                    type="email"
                    variant="outlined"
                    class="mb-2"
                    :disabled="!!editingCompany"
                    :error-messages="companyFormErrors.contact_email || companyFormErrors.email"
                  />
                  <v-text-field
                    v-model="companyForm.password"
                    :label="editingCompany ? 'Новый пароль (оставьте пустым, чтобы не менять)' : 'Пароль (необяз. — сгенерируется)'"
                    type="password"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.contact_phone"
                    label="Телефон *"
                    variant="outlined"
                    class="mb-2"
                    hint="Формат: 7 XXX XXX XX XX или +7 XXX XXX XX XX (плюс необязателен)"
                    persistent-hint
                    :error-messages="companyFormErrors.contact_phone"
                  />
                  <v-textarea
                    v-model="companyForm.address"
                    label="Адрес *"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="companyForm.legal_address"
                    label="Юридический адрес (необяз.)"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.inn"
                    label="ИНН (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.kpp"
                    label="КПП (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.ogrn"
                    label="ОГРН (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.bank_account"
                    label="Расчётный счёт (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.bank_name"
                    label="Название банка (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.bik"
                    label="БИК (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.corr_account"
                    label="Корр. счёт (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.website"
                    label="Сайт (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="companyForm.description"
                    label="Описание (необяз.)"
                    variant="outlined"
                    rows="2"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="companyDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingCompany" @click="saveCompany">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog
              v-model="deleteCompanyDialog"
              :fullscreen="fullscreenModal"
              max-width="400"
              persistent
            >
              <v-card>
                <v-card-title>Удалить компанию?</v-card-title>
                <v-card-text>
                  Будет удалена компания «{{ companyToDelete?.company_name }}» и все связанные организации. Действие нельзя отменить.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteCompanyDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingCompany" @click="doDeleteCompany">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Institutions -->
          <v-window-item value="institutions">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center flex-wrap">
                Все организации
                <v-spacer />
                <v-text-field
                  v-model="institutionSearchName"
                  density="compact"
                  hide-details
                  label="Поиск по названию"
                  variant="outlined"
                  clearable
                  style="max-width: 220px"
                  class="mr-2"
                />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openInstitutionDialog()">
                  Добавить организацию
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="institutionHeaders"
                :items="filteredInstitutions"
                :loading="loadingInstitutions"
                item-value="id"
              >
                <template #item.contacts="{ item }">
                  {{ item.contact_person }} / {{ item.phone }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openInstitutionCard(item)">Просмотр</v-btn>
                  <v-btn size="small" variant="text" @click="openInstitutionDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteInstitution(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog
              v-model="institutionCardDialog"
              :fullscreen="fullscreenModal"
              max-width="640"
              persistent
            >
              <v-card v-if="institutionCard">
                <v-card-title class="d-flex align-center">
                  Карточка организации
                  <v-spacer />
                  <v-btn icon variant="text" @click="institutionCardDialog = false">×</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="text-body-2">
                  <p><strong>Название:</strong> {{ institutionCard.institution_name }}</p>
                  <p><strong>Компания:</strong> {{ institutionCard.parent_company_name }}</p>
                  <p><strong>Тип:</strong> {{ institutionCard.institution_type }}</p>
                  <p><strong>Почта / Логин:</strong> {{ institutionCard.email }}</p>
                  <p><strong>Контактное лицо:</strong> {{ institutionCard.contact_person }}</p>
                  <p><strong>Телефон:</strong> {{ institutionCard.phone }}</p>
                  <p><strong>Адрес:</strong> {{ institutionCard.address || '—' }}</p>
                  <p><strong>Юр. адрес:</strong> {{ institutionCard.legal_address || '—' }}</p>
                  <p><strong>ИНН:</strong> {{ institutionCard.inn || '—' }}</p>
                  <p><strong>КПП:</strong> {{ institutionCard.kpp || '—' }}</p>
                  <p><strong>Контакт на площадке:</strong> {{ institutionCard.contact_person_on_site || '—' }}</p>
                  <p><strong>Телефон на площадке:</strong> {{ institutionCard.phone_on_site || '—' }}</p>
                  <p><strong>Предпочтительные дни:</strong> {{ institutionCard.preferred_days || '—' }}</p>
                  <p><strong>Предпочтительные часы:</strong> {{ institutionCard.preferred_hours || '—' }}</p>
                  <p v-if="institutionCard.access_details"><strong>Детали доступа:</strong><br />{{ institutionCard.access_details }}</p>
                  <p v-if="institutionCard.container_location"><strong>Расположение контейнера:</strong><br />{{ institutionCard.container_location }}</p>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn color="primary" @click="institutionCardDialog = false; openInstitutionDialog(institutionCard)">Изменить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog
              v-model="institutionDialog"
              :fullscreen="fullscreenModal"
              max-width="600"
              persistent
              scrollable
            >
              <v-card>
                <v-card-title>{{ editingInstitution ? 'Редактировать организацию' : 'Новая организация' }}</v-card-title>
                <v-card-text style="max-height: 70vh" class="overflow-y-auto">
                  <v-alert v-if="Object.keys(institutionFormErrors).length" type="error" density="compact" class="mb-2">
                    <div v-for="(msgs, key) in institutionFormErrors" :key="key">
                      {{ Array.isArray(msgs) ? msgs.join(' ') : msgs }}
                    </div>
                  </v-alert>
                  <v-select
                    v-model="institutionForm.parent_company"
                    :items="companies"
                    item-title="company_name"
                    item-value="id"
                    label="Компания (заявки идут только в эту компанию) *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.email"
                    label="Почта / Логин (для входа) *"
                    type="email"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.password"
                    :label="editingInstitution ? 'Новый пароль (оставьте пустым, чтобы не менять)' : 'Пароль (необяз. — сгенерируется)'"
                    type="password"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.institution_name"
                    label="Название учреждения *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.institution_type"
                    label="Тип организации *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="institutionForm.address"
                    label="Адрес *"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.contact_person"
                    label="Контактное лицо *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.phone"
                    label="Телефон *"
                    variant="outlined"
                    hint="Формат: 7 XXX XXX XX XX или +7 XXX XXX XX XX (плюс необязателен)"
                    persistent-hint
                    class="mb-2"
                    :error-messages="institutionFormErrors.phone"
                  />
                  <v-textarea
                    v-model="institutionForm.legal_address"
                    label="Юридический адрес (необяз.)"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.inn"
                    label="ИНН (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.kpp"
                    label="КПП (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.contact_person_on_site"
                    label="Контакт на площадке (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.phone_on_site"
                    label="Телефон на площадке (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.preferred_days"
                    label="Предпочтительные дни (необяз.)"
                    variant="outlined"
                    placeholder="пн, ср, пт"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.preferred_hours"
                    label="Предпочтительные часы (необяз.)"
                    variant="outlined"
                    placeholder="09:00-18:00"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="institutionForm.access_details"
                    label="Детали доступа (необяз.)"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="institutionForm.container_location"
                    label="Расположение контейнера (необяз.)"
                    variant="outlined"
                    rows="2"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="institutionDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingInstitution" @click="saveInstitution">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog
              v-model="deleteInstitutionDialog"
              :fullscreen="fullscreenModal"
              max-width="400"
              persistent
            >
              <v-card>
                <v-card-title>Удалить организацию?</v-card-title>
                <v-card-text>
                  Будет удалена организация «{{ institutionToDelete?.institution_name }}». Действие нельзя отменить.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteInstitutionDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingInstitution" @click="doDeleteInstitution">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <v-window-item value="registration-institutions">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Заявки на регистрацию учреждений
                <v-spacer />
                <v-btn variant="outlined" size="small" :loading="loadingRegistrationRequests" @click="loadRegistrationRequests">
                  Обновить
                </v-btn>
              </v-card-title>
              <v-card-text class="text-body-2 text-medium-emphasis">
                Учреждения, которые хотят сдавать вторсырьё. Создайте организацию в разделе «Организации» и привяжите к компании.
              </v-card-text>
              <v-divider />
              <v-data-table
                :headers="registrationRequestHeaders"
                :items="registrationRequests"
                :loading="loadingRegistrationRequests"
                item-value="id"
              >
                <template #item.created_at="{ item }">
                  {{ formatDate(item.created_at) }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openInstitutionRegistrationCard(item)">
                    Просмотр
                  </v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog
              v-model="institutionRegistrationCardDialog"
              :fullscreen="fullscreenModal"
              max-width="640"
              persistent
              scrollable
            >
              <v-card v-if="institutionRegistrationCard">
                <v-card-title class="d-flex align-center">
                  Заявка на регистрацию учреждения #{{ institutionRegistrationCard.id }}
                  <v-spacer />
                  <v-btn icon variant="text" @click="institutionRegistrationCardDialog = false">×</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="text-body-2 admin-reg-detail">
                  <p><strong>Учреждение:</strong> {{ institutionRegistrationCard.institution_name }}</p>
                  <p>
                    <strong>Контакт:</strong>
                    {{ institutionRegistrationCard.first_name }}
                    {{ institutionRegistrationCard.patronymic }}
                  </p>
                  <p><strong>Адрес:</strong> {{ institutionRegistrationCard.address || '—' }}</p>
                  <p>
                    <strong>Телефон:</strong>
                    <a
                      v-if="institutionRegistrationCard.phone"
                      :href="`tel:${institutionRegistrationCard.phone}`"
                      class="admin-reg-detail__link"
                    >{{ institutionRegistrationCard.phone }}</a>
                    <span v-else>—</span>
                  </p>
                  <p>
                    <strong>Email:</strong>
                    <a
                      v-if="institutionRegistrationCard.email"
                      :href="`mailto:${institutionRegistrationCard.email}`"
                      class="admin-reg-detail__link"
                    >{{ institutionRegistrationCard.email }}</a>
                    <span v-else>—</span>
                  </p>
                  <p><strong>Дата заявки:</strong> {{ formatDate(institutionRegistrationCard.created_at) }}</p>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn color="primary" @click="institutionRegistrationCardDialog = false">Закрыть</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <v-window-item value="registration-companies">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Заявки на регистрацию компаний (вывоз)
                <v-spacer />
                <v-btn variant="outlined" size="small" :loading="loadingCompanyRegistrationRequests" @click="loadCompanyRegistrationRequests">
                  Обновить
                </v-btn>
              </v-card-title>
              <v-card-text class="text-body-2 text-medium-emphasis">
                Компании, которые хотят заниматься вывозом вторсырья на платформе «Зелёный счёт».
              </v-card-text>
              <v-divider />
              <v-data-table
                :headers="companyRegistrationHeaders"
                :items="companyRegistrationRequests"
                :loading="loadingCompanyRegistrationRequests"
                item-value="id"
              >
                <template #item.created_at="{ item }">
                  {{ formatDate(item.created_at) }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openCompanyRegistrationCard(item)">
                    Просмотр
                  </v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog
              v-model="companyRegistrationCardDialog"
              :fullscreen="fullscreenModal"
              max-width="640"
              persistent
              scrollable
            >
              <v-card v-if="companyRegistrationCard">
                <v-card-title class="d-flex align-center">
                  Заявка на регистрацию компании #{{ companyRegistrationCard.id }}
                  <v-spacer />
                  <v-btn icon variant="text" @click="companyRegistrationCardDialog = false">×</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="text-body-2 admin-reg-detail">
                  <p><strong>Компания:</strong> {{ companyRegistrationCard.company_name }}</p>
                  <p><strong>Контактное лицо:</strong> {{ companyRegistrationCard.contact_name || '—' }}</p>
                  <p>
                    <strong>Телефон:</strong>
                    <a
                      v-if="companyRegistrationCard.phone"
                      :href="`tel:${companyRegistrationCard.phone}`"
                      class="admin-reg-detail__link"
                    >{{ companyRegistrationCard.phone }}</a>
                    <span v-else>—</span>
                  </p>
                  <p>
                    <strong>Email:</strong>
                    <a
                      v-if="companyRegistrationCard.email"
                      :href="`mailto:${companyRegistrationCard.email}`"
                      class="admin-reg-detail__link"
                    >{{ companyRegistrationCard.email }}</a>
                    <span v-else>—</span>
                  </p>
                  <p><strong>Регион / адрес:</strong> {{ companyRegistrationCard.address || '—' }}</p>
                  <p v-if="companyRegistrationCard.comment">
                    <strong>Комментарий:</strong><br />
                    {{ companyRegistrationCard.comment }}
                  </p>
                  <p v-else><strong>Комментарий:</strong> —</p>
                  <p><strong>Дата заявки:</strong> {{ formatDate(companyRegistrationCard.created_at) }}</p>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn color="primary" @click="companyRegistrationCardDialog = false">Закрыть</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Public pickup requests (homepage calculator) -->
          <v-window-item value="pickup-requests">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Заявки на вывоз с сайта
                <v-spacer />
                <v-btn variant="outlined" size="small" :loading="loadingPickupRequests" @click="loadPickupRequests">
                  Обновить
                </v-btn>
              </v-card-title>
              <v-card-text class="text-body-2 text-medium-emphasis">
                Заявки без личного кабинета: калькулятор на главной. Свяжитесь с клиентом и при необходимости создайте организацию в системе.
              </v-card-text>
              <v-divider />
              <v-data-table
                :headers="pickupRequestHeaders"
                :items="pickupRequests"
                :loading="loadingPickupRequests"
                item-value="id"
              >
                <template #item.created_at="{ item }">
                  {{ formatDate(item.created_at) }}
                </template>
                <template #item.preferred_date="{ item }">
                  {{ formatDateOnly(item.preferred_date) }}
                </template>
                <template #item.estimated_payout="{ item }">
                  {{ item.estimated_payout }} ₽
                </template>
                <template #item.materials_summary="{ item }">
                  {{ item.materials_summary }}
                </template>
                <template #item.total_weight_kg="{ item }">
                  {{ item.total_weight_kg }} кг
                </template>
                <template #item.status="{ item }">
                  <v-select
                    :model-value="item.status"
                    :items="pickupStatusOptions"
                    item-title="title"
                    item-value="value"
                    density="compact"
                    hide-details
                    variant="outlined"
                    style="max-width: 160px"
                    @update:model-value="(v) => updatePickupStatus(item, v as PublicPickupStatus)"
                  />
                </template>
                <template #item.actions="{ item }">
                  <div class="d-flex flex-wrap ga-1">
                    <v-btn size="small" variant="text" @click="openPickupRequestCard(item)">Просмотр</v-btn>
                    <v-btn size="small" variant="text" @click="openPickupNotes(item)">Заметки</v-btn>
                  </div>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog
              v-model="pickupRequestCardDialog"
              :fullscreen="fullscreenModal"
              max-width="720"
              persistent
              scrollable
            >
              <v-card v-if="pickupRequestCard">
                <v-card-title class="d-flex align-center">
                  Заявка на вывоз #{{ pickupRequestCard.id }}
                  <v-spacer />
                  <v-btn icon variant="text" @click="pickupRequestCardDialog = false">×</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="text-body-2 admin-reg-detail">
                  <p>
                    <strong>Статус:</strong>
                    {{ pickupRequestCard.status_display || pickupStatusLabel(pickupRequestCard.status) }}
                  </p>
                  <p>
                    <strong>Контакт:</strong>
                    {{ pickupRequestCard.contact_name || '—' }}
                  </p>
                  <p>
                    <strong>Телефон:</strong>
                    <a
                      v-if="pickupRequestCard.phone"
                      :href="`tel:${pickupRequestCard.phone}`"
                      class="admin-reg-detail__link"
                    >{{ pickupRequestCard.phone }}</a>
                    <span v-else>—</span>
                  </p>
                  <p><strong>Адрес вывоза:</strong> {{ pickupRequestCard.address || '—' }}</p>
                  <p><strong>Желаемая дата:</strong> {{ formatDateOnly(pickupRequestCard.preferred_date) }}</p>
                  <p><strong>Дата заявки:</strong> {{ formatDate(pickupRequestCard.created_at) }}</p>

                  <p class="mb-2"><strong>Сырьё:</strong></p>
                  <v-table v-if="pickupRequestCard.lines?.length" density="compact" class="admin-pickup-lines mb-3">
                    <thead>
                      <tr>
                        <th>Материал</th>
                        <th class="text-end">Вес</th>
                        <th class="text-end">Сумма</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="line in pickupRequestCard.lines" :key="line.id">
                        <td>{{ line.material_name }}</td>
                        <td class="text-end">{{ line.weight_kg }} кг</td>
                        <td class="text-end">{{ line.line_payout }} ₽</td>
                      </tr>
                    </tbody>
                    <tfoot>
                      <tr>
                        <th>Итого</th>
                        <th class="text-end">{{ pickupRequestCard.total_weight_kg }} кг</th>
                        <th class="text-end">{{ pickupRequestCard.estimated_payout }} ₽</th>
                      </tr>
                    </tfoot>
                  </v-table>
                  <p v-else class="mb-3">{{ pickupRequestCard.materials_summary || '—' }}</p>

                  <p v-if="pickupRequestCard.admin_notes">
                    <strong>Заметки администратора:</strong><br />
                    {{ pickupRequestCard.admin_notes }}
                  </p>
                  <p v-else><strong>Заметки администратора:</strong> —</p>
                </v-card-text>
                <v-card-actions>
                  <v-btn variant="text" @click="openPickupNotes(pickupRequestCard)">Редактировать заметки</v-btn>
                  <v-spacer />
                  <v-btn color="primary" @click="pickupRequestCardDialog = false">Закрыть</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="pickupNotesDialog" max-width="480" persistent>
              <v-card>
                <v-card-title>Заметки администратора</v-card-title>
                <v-card-text>
                  <v-textarea v-model="pickupNotesForm" label="Заметки" rows="4" variant="outlined" />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="pickupNotesDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingPickupNotes" @click="savePickupNotes">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Requests -->
          <v-window-item value="requests">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center flex-wrap ga-2">
                Все заявки
                <v-select
                  v-model="requestStatusFilter"
                  :items="requestStatusOptions"
                  density="compact"
                  hide-details
                  label="Статус"
                  variant="outlined"
                  style="max-width: 140px"
                />
                <v-select
                  v-model="requestDateFilter"
                  :items="requestDateFilterOptions"
                  item-title="title"
                  item-value="value"
                  density="compact"
                  hide-details
                  label="Дата"
                  variant="outlined"
                  style="max-width: 180px"
                />
                <v-text-field
                  v-if="requestDateFilter === 'range'"
                  v-model="requestDateFrom"
                  type="date"
                  density="compact"
                  hide-details
                  label="С"
                  variant="outlined"
                  clearable
                  style="max-width: 160px"
                />
                <v-text-field
                  v-if="requestDateFilter === 'range'"
                  v-model="requestDateTo"
                  type="date"
                  density="compact"
                  hide-details
                  label="По"
                  variant="outlined"
                  clearable
                  style="max-width: 160px"
                />
                <v-text-field
                  v-model="requestInstitutionFilter"
                  density="compact"
                  hide-details
                  label="Организация"
                  variant="outlined"
                  clearable
                  style="max-width: 200px"
                />
                <v-text-field
                  v-model="requestCompanyFilter"
                  density="compact"
                  hide-details
                  label="Компания"
                  variant="outlined"
                  clearable
                  style="max-width: 200px"
                />
                <v-spacer />
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="requestHeaders"
                :items="filteredAdminRequests"
                :loading="loadingRequests"
                item-value="id"
              >
                <template #item.request_number="{ item }">
                  {{ item.request_number || item.id }}
                </template>
                <template #item.status="{ item }">
                  <v-chip :color="requestStatusColor(item.status)" size="small">
                    {{ requestStatusLabel(item.status) }}
                  </v-chip>
                </template>
                <template #item.estimated_value="{ item }">
                  {{ item.estimated_value != null ? `${item.estimated_value} руб.` : '—' }}
                </template>
                <template #item.actual_value="{ item }">
                  {{ item.actual_value != null ? `${item.actual_value} руб.` : '—' }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openRequestCard(item)">Просмотр</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog
              v-model="requestCardDialog"
              :fullscreen="fullscreenModal"
              max-width="640"
              persistent
            >
              <v-card v-if="requestCard">
                <v-card-title class="d-flex align-center">
                  Заявка {{ requestCard.request_number || requestCard.id }}
                  <v-spacer />
                  <v-btn icon variant="text" @click="requestCardDialog = false">×</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="text-body-2">
                  <p><strong>Организация:</strong> {{ requestCard.institution_name }}</p>
                  <p><strong>Компания:</strong> {{ requestCard.receiving_company_name }}</p>
                  <p><strong>Статус:</strong> {{ requestStatusLabel(requestCard.status) }}</p>
                  <p><strong>Тип макулатуры:</strong> {{ requestCard.material_type_display || requestCard.material_type || '—' }}</p>
                  <p><strong>Вес (кг):</strong> {{ requestCard.estimated_amount ?? requestCard.paper_weight_kg ?? '—' }}</p>
                  <p><strong>Ориент. стоимость:</strong> {{ requestCard.estimated_value != null ? `${requestCard.estimated_value} руб.` : '—' }}</p>
                  <p><strong>Факт. стоимость:</strong> {{ requestCard.actual_value != null ? `${requestCard.actual_value} руб.` : '—' }}</p>
                  <p><strong>Желаемая дата:</strong> {{ requestCard.desired_date || '—' }}</p>
                  <p><strong>Комментарий:</strong> {{ requestCard.comment || '—' }}</p>
                  <p><strong>Дата создания:</strong> {{ requestCard.created_at }}</p>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn color="primary" @click="requestCardDialog = false">Закрыть</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Statistics (advanced analytics dashboard) -->
          <v-window-item value="statistics">
            <AdminStatsDashboard />
          </v-window-item>

          <!-- Bonuses -->
          <v-window-item value="bonuses">
            <v-card class="rounded-lg elevation-1 mb-4">
              <v-card-title class="d-flex align-center">
                <v-icon class="mr-2">mdi-percent</v-icon>
                Процент бонуса от суммы заявки
              </v-card-title>
              <v-card-text>
                <v-row align="center">
                  <v-col cols="12" sm="4" md="3">
                    <v-text-field
                      v-model.number="bonusConfigForm.bonus_percent"
                      label="Процент (%)"
                      type="number"
                      min="0"
                      max="100"
                      step="0.01"
                      variant="outlined"
                      density="compact"
                      hide-details
                    />
                  </v-col>
                  <v-col cols="12" sm="4">
                    <v-btn color="primary" :loading="savingBonusConfig" @click="saveBonusConfig">
                      Сохранить
                    </v-btn>
                  </v-col>
                </v-row>
                <p class="text-caption text-medium-emphasis mt-2">
                  Бонус начисляется организациям после завершения заявки. Сумма = стоимость заявки × процент. Администратор подтверждает или меняет сумму и начисляет бонус.
                </p>
              </v-card-text>
            </v-card>
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center flex-wrap ga-2">
                Бонусы организаций
                <v-select
                  v-model="bonusStatusFilter"
                  :items="bonusStatusOptions"
                  density="compact"
                  hide-details
                  label="Статус"
                  variant="outlined"
                  style="max-width: 180px"
                />
                <v-spacer />
                <v-btn variant="tonal" size="small" @click="fetchInstitutionBonuses">Обновить</v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="bonusHeaders"
                :items="filteredBonuses"
                :loading="loadingBonuses"
                item-value="id"
              >
                <template #item.order_value="{ item }">
                  {{ item.order_value != null ? `${item.order_value} (стоимость заявки)` : '—' }}
                </template>
                <template #item.calculated_amount="{ item }">
                  {{ item.calculated_amount }} баллов
                </template>
                <template #item.awarded_amount="{ item }">
                  {{ item.awarded_amount != null ? `${item.awarded_amount} баллов` : '—' }}
                </template>
                <template #item.status="{ item }">
                  <v-chip :color="item.status === 'confirmed' ? 'success' : 'warning'" size="small">
                    {{ item.status === 'confirmed' ? 'Начислен' : 'Ожидает' }}
                  </v-chip>
                </template>
                <template #item.actions="{ item }">
                  <v-btn
                    v-if="item.status === 'pending'"
                    size="small"
                    variant="text"
                    color="primary"
                    @click="openBonusAwardDialog(item)"
                  >
                    Подтвердить / изменить
                  </v-btn>
                  <span v-else class="text-medium-emphasis">—</span>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog
              v-model="bonusAwardDialog"
              :fullscreen="fullscreenModal"
              max-width="480"
              persistent
            >
              <v-card v-if="editingBonus">
                <v-card-title>Начисление бонуса</v-card-title>
                <v-card-text>
                  <p class="text-body-2 mb-3">
                    Организация: <strong>{{ editingBonus.institution_name }}</strong><br>
                    Заявка: {{ editingBonus.request_number }}<br>
                    Стоимость заявки: {{ editingBonus.order_value ?? '—' }} (для расчёта)<br>
                    Рассчитанная сумма бонуса: {{ editingBonus.calculated_amount }} баллов
                  </p>
                  <v-text-field
                    v-model.number="bonusAwardForm.awarded_amount"
                    label="Сумма к начислению (баллы)"
                    type="number"
                    min="0"
                    step="0.01"
                    variant="outlined"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="bonusAwardDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingBonusAward" @click="confirmBonusAward">
                    Начислить бонус
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Technical support -->
          <v-window-item value="support">
            <v-card class="rounded-lg elevation-1 mb-4">
              <v-card-title class="d-flex align-center">
                <v-icon class="mr-2">mdi-headset</v-icon>
                Аккаунт техподдержки
              </v-card-title>
              <v-card-text>
                <v-alert v-if="supportUsers.length" type="info" variant="tonal" density="compact" class="mb-4">
                  Активный специалист: <strong>{{ supportConfig.support_username || supportUsers[0]?.username }}</strong>
                  · привязано учреждений: <strong>{{ supportConfig.institutions_assigned ?? 0 }}</strong>
                </v-alert>
                <v-row v-if="!supportUsers.length">
                  <v-col cols="12" md="5">
                    <v-text-field
                      v-model="supportCreateForm.email"
                      label="Email (логин)"
                      type="email"
                      variant="outlined"
                      class="mb-3"
                    />
                  </v-col>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="supportCreateForm.password"
                      label="Пароль (необяз. — сгенерируется)"
                      type="password"
                      variant="outlined"
                      class="mb-3"
                    />
                  </v-col>
                  <v-col cols="12" md="3" class="d-flex align-center">
                    <v-btn color="primary" :loading="creatingSupportUser" @click="createSupportUser">
                      Создать аккаунт
                    </v-btn>
                  </v-col>
                </v-row>
                <div v-else class="d-flex flex-wrap ga-3 align-center">
                  <v-btn
                    color="primary"
                    variant="tonal"
                    :loading="assigningSupport"
                    @click="assignSupportToAll"
                  >
                    Назначить на все учреждения
                  </v-btn>
                  <v-btn variant="text" href="/support" target="_blank">Открыть панель поддержки</v-btn>
                </div>
                <p class="text-caption text-medium-emphasis mt-3">
                  В системе может быть один аккаунт техподдержки. Он видит чаты всех учреждений. Новые организации привязываются автоматически.
                </p>
              </v-card-text>
            </v-card>
          </v-window-item>

          <!-- Products (points catalog) -->
          <v-window-item value="products">
            <v-card class="rounded-lg mb-4" elevation="1">
              <v-card-title class="d-flex align-center">
                Категории товаров
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" size="small" @click="openCategoryDialog()">Добавить категорию</v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="categoryHeaders"
                :items="productCategories"
                :loading="loadingCategories"
                item-value="id"
                density="compact"
              >
                <template #item.is_active="{ item }">
                  <v-chip :color="item.is_active ? 'success' : 'default'" size="small">{{ item.is_active ? 'Да' : 'Нет' }}</v-chip>
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openCategoryDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteCategory(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Товары за баллы (каталог для организаций)
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openProductDialog()">Добавить товар</v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="productHeaders"
                :items="products"
                :loading="loadingProducts"
                item-value="id"
              >
                <template #item.category_name="{ item }">{{ item.category_name || '—' }}</template>
                <template #item.image_url="{ item }">
                <v-img v-if="resolveMediaUrl(item.image_url)" :src="resolveMediaUrl(item.image_url)" width="40" height="40" class="rounded" cover />
                <span v-else class="text-medium-emphasis">—</span>
              </template>
                <template #item.price_in_points="{ item }">{{ item.price_in_points }} баллов</template>
                <template #item.is_active="{ item }">
                  <v-chip :color="item.is_active ? 'success' : 'default'" size="small">{{ item.is_active ? 'Да' : 'Нет' }}</v-chip>
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openProductDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteProduct(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>
            <v-dialog
              v-model="productDialog"
              :fullscreen="fullscreenModal"
              max-width="500"
              persistent
            >
              <v-card>
                <v-card-title>{{ editingProduct ? 'Редактировать товар' : 'Новый товар' }}</v-card-title>
                <v-card-text>
                  <v-select
                    v-model="productForm.category"
                    :items="categorySelectItems"
                    label="Категория"
                    variant="outlined"
                    class="mb-3"
                    clearable
                  />
                  <v-text-field v-model="productForm.name" label="Название" variant="outlined" class="mb-3" />
                  <v-textarea v-model="productForm.description" label="Описание" variant="outlined" class="mb-3" rows="3" />
                  <v-file-input
                    v-model="productForm.imageFile"
                    label="Фото товара"
                    variant="outlined"
                    class="mb-3"
                    accept="image/*"
                    prepend-icon=""
                    prepend-inner-icon="mdi-camera"
                    clearable
                    show-size
                  />
                  <v-img v-if="productForm.imagePreview" :src="productForm.imagePreview" max-height="120" class="mb-3 rounded" />
                  <v-text-field v-model.number="productForm.price_in_points" label="Цена (баллы)" type="number" min="0" step="0.01" variant="outlined" class="mb-3" />
                  <v-checkbox v-model="productForm.is_active" label="Активен (виден в каталоге)" />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="productDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingProduct" @click="saveProduct">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
            <v-dialog
              v-model="deleteProductDialog"
              :fullscreen="fullscreenModal"
              max-width="400"
              persistent
            >
              <v-card>
                <v-card-title>Удалить товар?</v-card-title>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteProductDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingProduct" @click="doDeleteProduct">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
            <v-dialog v-model="categoryDialog" :fullscreen="fullscreenModal" max-width="480" persistent>
              <v-card>
                <v-card-title>{{ editingCategory ? 'Редактировать категорию' : 'Новая категория' }}</v-card-title>
                <v-card-text>
                  <v-text-field v-model="categoryForm.name" label="Название" variant="outlined" class="mb-3" />
                  <v-text-field v-model="categoryForm.slug" label="Slug (латиница)" variant="outlined" class="mb-3" hint="Например: office, eco" persistent-hint />
                  <v-text-field v-model.number="categoryForm.sort_order" label="Порядок сортировки" type="number" variant="outlined" class="mb-3" />
                  <v-checkbox v-model="categoryForm.is_active" label="Активна" />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="categoryDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingCategory" @click="saveCategory">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
            <v-dialog v-model="deleteCategoryDialog" :fullscreen="fullscreenModal" max-width="400" persistent>
              <v-card>
                <v-card-title>Удалить категорию?</v-card-title>
                <v-card-text>Товары останутся без категории.</v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteCategoryDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingCategory" @click="doDeleteCategory">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Points orders (bonus orders) -->
          <v-window-item value="points-orders">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center flex-wrap ga-2">
                Заказы на баллы
                <v-select
                  v-model="pointsOrderStatusFilter"
                  :items="pointsOrderStatusOptions"
                  density="compact"
                  hide-details
                  label="Статус"
                  variant="outlined"
                  style="max-width: 160px"
                />
                <v-spacer />
                <v-btn variant="tonal" size="small" @click="loadPointsOrders">Обновить</v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="pointsOrderHeaders"
                :items="filteredPointsOrders"
                :loading="loadingPointsOrders"
                item-value="id"
              >
                <template #item.total_points="{ item }">{{ item.total_points }} баллов</template>
                <template #item.status="{ item }">
                  <v-chip :color="pointsOrderStatusColor(item.status)" size="small">{{ pointsOrderStatusLabel(item.status) }}</v-chip>
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openPointsOrderDetail(item)">Просмотр</v-btn>
                </template>
              </v-data-table>
            </v-card>
            <v-dialog
              v-model="pointsOrderDetailDialog"
              :fullscreen="fullscreenModal"
              max-width="600"
              persistent
            >
              <v-card v-if="selectedPointsOrder">
                <v-card-title class="d-flex align-center">
                  Заказ #{{ selectedPointsOrder.id }}
                  <v-spacer />
                  <v-btn icon variant="text" @click="pointsOrderDetailDialog = false">×</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text>
                  <p class="text-subtitle-2 mb-1">Организация</p>
                  <p class="mb-3">{{ selectedPointsOrder.institution_name }}</p>
                  <p class="text-subtitle-2 mb-1">Получатель</p>
                  <p class="mb-1">{{ selectedPointsOrder.recipient_name }}, {{ selectedPointsOrder.recipient_phone }}</p>
                  <p class="mb-3 text-body-2">{{ selectedPointsOrder.address }}</p>
                  <p class="text-subtitle-2 mb-1">Состав заказа (корзина)</p>
                  <v-table density="compact" class="mb-3">
                    <thead>
                      <tr>
                        <th>Товар</th>
                        <th>Кол-во</th>
                        <th>Цена (баллы)</th>
                        <th>Сумма</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="line in selectedPointsOrder.lines" :key="line.id">
                        <td>{{ line.product_name }}</td>
                        <td>{{ line.quantity }}</td>
                        <td>{{ line.price_at_order }}</td>
                        <td>{{ (parseFloat(line.price_at_order) * line.quantity).toFixed(2) }}</td>
                      </tr>
                    </tbody>
                  </v-table>
                  <p class="text-body-1 font-weight-bold">Итого: {{ selectedPointsOrder.total_points }} баллов</p>
                  <v-select
                    v-model="pointsOrderStatusEdit"
                    :items="pointsOrderStatusOptions"
                    label="Статус заказа"
                    variant="outlined"
                    class="mt-3"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="pointsOrderDetailDialog = false">Закрыть</v-btn>
                  <v-btn color="primary" :loading="savingPointsOrderStatus" @click="savePointsOrderStatus">Сохранить статус</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <v-window-item value="audit-logs">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center flex-wrap ga-2">
                Логи действий
                <v-select
                  v-model="auditCategoryFilter"
                  :items="auditCategoryOptions"
                  density="compact"
                  hide-details
                  label="Категория"
                  variant="outlined"
                  style="max-width: 160px"
                />
                <v-select
                  v-model="auditRoleFilter"
                  :items="auditRoleOptions"
                  density="compact"
                  hide-details
                  label="Роль"
                  variant="outlined"
                  style="max-width: 180px"
                />
                <v-text-field
                  v-model="auditSearch"
                  density="compact"
                  hide-details
                  clearable
                  label="Поиск"
                  variant="outlined"
                  style="max-width: 220px"
                />
                <v-spacer />
                <v-btn variant="outlined" size="small" @click="exportAuditLogs('csv')">Экспорт CSV</v-btn>
                <v-btn variant="outlined" size="small" @click="exportAuditLogs('txt')">Экспорт TXT</v-btn>
                <v-btn variant="tonal" size="small" @click="loadAuditLogs">Обновить</v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="auditLogHeaders"
                :items="auditLogs"
                :loading="loadingAuditLogs"
                item-value="id"
              >
                <template #item.created_at="{ item }">{{ formatDate(item.created_at) }}</template>
                <template #item.category="{ item }">
                  <v-chip :color="auditCategoryColor(item.category)" size="small" variant="tonal">
                    {{ item.category }}
                  </v-chip>
                </template>
              </v-data-table>
              <v-card-actions class="d-flex align-center justify-space-between">
                <span class="text-body-2">Всего: {{ auditTotal }}</span>
                <div class="d-flex ga-2">
                  <v-btn size="small" variant="text" :disabled="auditPage <= 1" @click="auditPage -= 1">Назад</v-btn>
                  <span class="text-body-2 align-self-center">Стр. {{ auditPage }} / {{ auditPages }}</span>
                  <v-btn size="small" variant="text" :disabled="auditPage >= auditPages" @click="auditPage += 1">Вперёд</v-btn>
                </div>
              </v-card-actions>
            </v-card>
          </v-window-item>

          <v-window-item value="database-info">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Информация о базе данных
                <v-spacer />
                <v-btn variant="tonal" size="small" @click="loadDatabaseInfo">Обновить</v-btn>
              </v-card-title>
              <v-divider />
              <v-card-text>
                <v-alert v-if="databaseInfoError" type="error" density="compact" class="mb-4">
                  {{ databaseInfoError }}
                </v-alert>
                <div v-else-if="databaseInfo">
                  <p><strong>Тип:</strong> {{ databaseInfo.db_type }}</p>
                  <p><strong>Engine:</strong> {{ databaseInfo.engine }}</p>
                  <p><strong>Name:</strong> {{ databaseInfo.name }}</p>
                  <p><strong>Host:</strong> {{ databaseInfo.host || 'localhost / file' }}</p>
                  <p><strong>Port:</strong> {{ databaseInfo.port || '—' }}</p>
                </div>
                <div v-else class="text-medium-emphasis">Нет данных.</div>
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { useBreakpoints } from '@/composables/useBreakpoints'
import type {
  CompanyProfile,
  InstitutionProfile,
  Material,
  CollectionRequest,
  NewsArticle,
  PriceList,
  PublicPickupRequest,
  PublicPickupStatus,
  InstitutionRegistrationRequest,
  CompanyRegistrationRequest,
} from '@/types'
import AdminStatsDashboard from '@/components/admin/AdminStatsDashboard.vue'
import AppHeaderLogo from '@/components/AppHeaderLogo.vue'
import { resolveMediaUrl } from '@/utils/mediaUrl'
import { pickFirstFile } from '@/utils/fileInput'
import { materialMdiIcon } from '@/utils/materialIcon'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()
const { fullscreenModal } = useBreakpoints()

const activeTab = ref('prices')
const prices = ref<PriceList[]>([])
const companies = ref<CompanyProfile[]>([])
const institutions = ref<InstitutionProfile[]>([])
const adminRequests = ref<CollectionRequest[]>([])
const loadingPrices = ref(false)
const loadingCompanies = ref(false)
const loadingInstitutions = ref(false)
const loadingRequests = ref(false)
const priceDialog = ref(false)
const editingPrice = ref<PriceList | null>(null)
const savingPrice = ref(false)
const priceForm = reactive({
  material: null as number | null,
  price_per_kg: '' as string | number,
  is_active: true,
})
const materialDialog = ref(false)
const editingMaterial = ref<Material | null>(null)
const savingMaterial = ref(false)
const materialForm = reactive({
  name: '',
  code: '',
  short_description: '',
  icon: '',
  sort_order: 0,
  is_active: true,
  iconImageFile: null as File | File[] | null,
  iconPreview: '' as string,
  imageFile: null as File | File[] | null,
  imagePreview: '' as string,
  clearIconImage: false,
  clearImage: false,
})
const materialFormErrors = ref<Record<string, string>>({})
const requestStatusFilter = ref('all')
type RequestDateFilter =
  | 'all'
  | 'today'
  | 'yesterday'
  | 'week'
  | 'month'
  | 'quarter'
  | 'half_year'
  | 'year'
  | 'range'
const requestDateFilter = ref<RequestDateFilter>('all')
const requestDateFrom = ref('')
const requestDateTo = ref('')
const requestDateFilterOptions = [
  { title: 'Все даты', value: 'all' },
  { title: 'Сегодня', value: 'today' },
  { title: 'Вчера', value: 'yesterday' },
  { title: 'Неделя (текущая)', value: 'week' },
  { title: 'Месяц (текущий)', value: 'month' },
  { title: 'Квартал (текущий)', value: 'quarter' },
  { title: 'Полгода (текущие)', value: 'half_year' },
  { title: 'Год (текущий)', value: 'year' },
  { title: 'Период…', value: 'range' },
]

const newsArticles = ref<NewsArticle[]>([])
const loadingNews = ref(false)
const newsDialog = ref(false)
const editingNews = ref<NewsArticle | null>(null)
const savingNews = ref(false)
const newsForm = reactive({
  title: '',
  content: '',
  imageFile: null as File | File[] | null,
  imagePreview: '' as string,
  is_published: true,
})
const deleteNewsDialog = ref(false)
const newsToDelete = ref<NewsArticle | null>(null)
const deletingNews = ref(false)

const newsHeaders = [
  { title: 'Заголовок', key: 'title' },
  { title: 'Дата', key: 'created_at', width: '140' },
  { title: 'Опубликовано', key: 'is_published', width: '120' },
  { title: 'Автор', key: 'author_username', width: '120' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const companyDialog = ref(false)
const editingCompany = ref<CompanyProfile | null>(null)
const savingCompany = ref(false)
const companyForm = reactive({
  company_name: '',
  contact_email: '',
  password: '',
  contact_phone: '',
  address: '',
  legal_address: '',
  inn: '',
  kpp: '',
  ogrn: '',
  bank_account: '',
  bank_name: '',
  bik: '',
  corr_account: '',
  website: '',
  description: '',
})
const deleteCompanyDialog = ref(false)
const companyToDelete = ref<CompanyProfile | null>(null)
const deletingCompany = ref(false)
const companyCardDialog = ref(false)
const companyCard = ref<CompanyProfile | null>(null)
const companyFormErrors = ref<Record<string, string[]>>({})
const snackbar = ref({ show: false, text: '', color: 'error' })
function showSnackbar(text: string, color: 'success' | 'error' | 'info') {
  snackbar.value = { show: true, text, color }
}

const institutionDialog = ref(false)
const editingInstitution = ref<InstitutionProfile | null>(null)
const savingInstitution = ref(false)
const institutionForm = reactive({
  parent_company: null as number | null,
  email: '',
  password: '',
  institution_name: '',
  institution_type: '',
  address: '',
  contact_person: '',
  phone: '',
  legal_address: '',
  inn: '',
  kpp: '',
  contact_person_on_site: '',
  phone_on_site: '',
  preferred_days: '',
  preferred_hours: '',
  access_details: '',
  container_location: '',
})
const deleteInstitutionDialog = ref(false)
const institutionToDelete = ref<InstitutionProfile | null>(null)
const deletingInstitution = ref(false)
const institutionFormErrors = ref<Record<string, string[]>>({})

const materials = ref<Material[]>([])
const loadingMaterials = ref(false)

const priceHeaders = [
  { title: 'Название', key: 'material_name', sortable: true },
  { title: 'Цена за кг', key: 'price_per_kg' },
  { title: 'Статус', key: 'is_active', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false, width: '200' },
]

const materialHeaders = [
  { title: 'Иконка', key: 'icon_url', sortable: false, width: '72' },
  { title: 'Фото', key: 'image_url', sortable: false, width: '80' },
  { title: 'Название', key: 'name', sortable: true },
  { title: 'Код', key: 'code', sortable: true },
  { title: 'Порядок', key: 'sort_order', width: '90' },
  { title: 'Статус', key: 'is_active', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false, width: '120' },
]

const materialSearch = ref('')
const priceFormError = ref('')
const priceFormErrors = ref<Record<string, string>>({})

const filteredPrices = computed(() => {
  let list = prices.value
  const q = (materialSearch.value || '').trim().toLowerCase()
  if (q) {
    list = list.filter(
      (p) =>
        (p.material_name || '').toLowerCase().includes(q) ||
        (p.material_code || '').toLowerCase().includes(q)
    )
  }
  return list
})

const filteredMaterialCatalog = computed(() => {
  let list = materials.value
  const q = (materialSearch.value || '').trim().toLowerCase()
  if (q) {
    list = list.filter(
      (m) =>
        (m.name || '').toLowerCase().includes(q) ||
        (m.code || '').toLowerCase().includes(q)
    )
  }
  return list
})

const availableMaterialsForPrice = computed(() => {
  const used = new Set(prices.value.map((p) => p.material))
  if (editingPrice.value) return materials.value
  return materials.value.filter((m) => m.is_active && !used.has(m.id))
})

const companyHeaders = [
  { title: 'Название', key: 'company_name' },
  { title: 'Контакты', key: 'contact_phone' },
  { title: 'Адрес', key: 'address' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const institutionHeaders = [
  { title: 'Название', key: 'institution_name' },
  { title: 'Компания', key: 'parent_company_name' },
  { title: 'Тип', key: 'institution_type' },
  { title: 'Контакты', key: 'contacts' },
  { title: 'Адрес', key: 'address' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const requestHeaders = [
  { title: 'Номер', key: 'request_number', width: '140' },
  { title: 'Организация', key: 'institution_name' },
  { title: 'Компания', key: 'receiving_company_name' },
  { title: 'Тип макулатуры', key: 'material_type_display' },
  { title: 'Вес (кг)', key: 'estimated_amount' },
  { title: 'Ориент. стоимость', key: 'estimated_value' },
  { title: 'Факт. стоимость', key: 'actual_value' },
  { title: 'Статус', key: 'status' },
  { title: 'Дата создания', key: 'created_at' },
  { title: 'Действия', key: 'actions', sortable: false, width: '100' },
]

const requestStatusOptions = [
  { title: 'Все', value: 'all' },
  { title: 'Новые', value: 'new' },
  { title: 'Принятые', value: 'accepted' },
  { title: 'Завершённые', value: 'completed' },
]

const institutionSearchName = ref('')
const requestInstitutionFilter = ref('')
const requestCompanyFilter = ref('')
const institutionCardDialog = ref(false)
const institutionCard = ref<InstitutionProfile | null>(null)
const requestCardDialog = ref(false)
const requestCard = ref<CollectionRequest | null>(null)

// Registration requests (from public homepage)
const registrationRequests = ref<InstitutionRegistrationRequest[]>([])
const loadingRegistrationRequests = ref(false)
const institutionRegistrationCardDialog = ref(false)
const institutionRegistrationCard = ref<InstitutionRegistrationRequest | null>(null)
const companyRegistrationRequests = ref<CompanyRegistrationRequest[]>([])
const loadingCompanyRegistrationRequests = ref(false)
const companyRegistrationCardDialog = ref(false)
const companyRegistrationCard = ref<CompanyRegistrationRequest | null>(null)
const companyRegistrationHeaders = [
  { title: 'Дата', key: 'created_at', width: '130' },
  { title: 'Компания', key: 'company_name' },
  { title: 'Контакт', key: 'contact_name' },
  { title: 'Телефон', key: 'phone', width: '120' },
  { title: 'Email', key: 'email' },
  { title: 'Действия', key: 'actions', sortable: false, width: '110' },
]
const registrationRequestHeaders = [
  { title: 'Дата', key: 'created_at', width: '130' },
  { title: 'Учреждение', key: 'institution_name' },
  { title: 'Контакт', key: 'first_name' },
  { title: 'Телефон', key: 'phone', width: '120' },
  { title: 'Email', key: 'email' },
  { title: 'Действия', key: 'actions', sortable: false, width: '110' },
]

const pickupRequests = ref<PublicPickupRequest[]>([])
const loadingPickupRequests = ref(false)
const pickupRequestHeaders = [
  { title: 'Дата', key: 'created_at', width: '130' },
  { title: 'Сырьё', key: 'materials_summary' },
  { title: 'Вес', key: 'total_weight_kg', width: '90' },
  { title: 'Сумма', key: 'estimated_payout', width: '100' },
  { title: 'Адрес', key: 'address' },
  { title: 'Телефон', key: 'phone', width: '120' },
  { title: 'Дата вывоза', key: 'preferred_date', width: '110' },
  { title: 'Статус', key: 'status', width: '180' },
  { title: 'Действия', key: 'actions', sortable: false, width: '160' },
]
const pickupRequestCardDialog = ref(false)
const pickupRequestCard = ref<PublicPickupRequest | null>(null)
const pickupStatusOptions = [
  { title: 'Новая', value: 'new' },
  { title: 'Связались', value: 'contacted' },
  { title: 'Выполнена', value: 'done' },
  { title: 'Отменена', value: 'cancelled' },
]
const pickupNotesDialog = ref(false)
const pickupNotesTarget = ref<PublicPickupRequest | null>(null)
const pickupNotesForm = ref('')
const savingPickupNotes = ref(false)

interface AuditLogItem {
  id: number
  created_at: string
  category: 'info' | 'warning' | 'critical' | string
  action_type: string
  actor_role: string
  actor_username: string
  target_model: string
  target_id: string
  short_summary: string
  ip_address: string
}
interface AuditLogsResponse {
  count: number
  page: number
  page_size: number
  results: AuditLogItem[]
}
interface DatabaseInfo {
  db_type: string
  engine: string
  name: string
  host: string
  port: string
}
const auditLogs = ref<AuditLogItem[]>([])
const loadingAuditLogs = ref(false)
const auditSearch = ref('')
const auditCategoryFilter = ref('all')
const auditRoleFilter = ref('all')
const auditPage = ref(1)
const auditPageSize = ref(25)
const auditTotal = ref(0)
const auditPages = computed(() => Math.max(1, Math.ceil(auditTotal.value / auditPageSize.value)))
const auditCategoryOptions = [
  { title: 'Все категории', value: 'all' },
  { title: 'Info', value: 'info' },
  { title: 'Warning', value: 'warning' },
  { title: 'Critical', value: 'critical' },
]
const auditRoleOptions = [
  { title: 'Все роли', value: 'all' },
  { title: 'Администратор', value: 'admin' },
  { title: 'Компания', value: 'company' },
  { title: 'Организация', value: 'institution' },
]
const auditLogHeaders = [
  { title: 'Дата', key: 'created_at', width: '170' },
  { title: 'Категория', key: 'category', width: '110' },
  { title: 'Действие', key: 'action_type', width: '150' },
  { title: 'Роль', key: 'actor_role', width: '120' },
  { title: 'Пользователь', key: 'actor_username', width: '170' },
  { title: 'Модель', key: 'target_model', width: '150' },
  { title: 'ID', key: 'target_id', width: '90' },
  { title: 'Сводка', key: 'short_summary' },
  { title: 'IP', key: 'ip_address', width: '130' },
]
const databaseInfo = ref<DatabaseInfo | null>(null)
const databaseInfoError = ref('')

// Bonuses
interface InstitutionBonusItem {
  id: number
  collection_request: number
  institution: number
  institution_name: string
  request_number: string
  order_value: string | null
  calculated_amount: string
  awarded_amount: string | null
  status: 'pending' | 'confirmed'
  confirmed_at: string | null
  confirmed_by: number | null
  created_at: string
}
const bonusConfigForm = reactive({ bonus_percent: 0 })
const savingBonusConfig = ref(false)
const bonusStatusFilter = ref('all')
const bonusStatusOptions = [
  { title: 'Все', value: 'all' },
  { title: 'Ожидают подтверждения', value: 'pending' },
  { title: 'Начислены', value: 'confirmed' },
]
const bonusHeaders = [
  { title: 'Организация', key: 'institution_name' },
  { title: 'Заявка', key: 'request_number', width: '140' },
  { title: 'Стоимость заявки', key: 'order_value' },
  { title: 'Рассчитано', key: 'calculated_amount' },
  { title: 'Начислено', key: 'awarded_amount' },
  { title: 'Статус', key: 'status' },
  { title: 'Действия', key: 'actions', sortable: false, width: '160' },
]
const institutionBonuses = ref<InstitutionBonusItem[]>([])
const loadingBonuses = ref(false)
const bonusAwardDialog = ref(false)
const editingBonus = ref<InstitutionBonusItem | null>(null)
const bonusAwardForm = reactive({ awarded_amount: 0 })
const savingBonusAward = ref(false)

// Technical support
interface SupportConfigItem {
  id: number
  support_user: number | null
  support_username: string
  support_email: string
  institutions_assigned: number
}
interface SupportUserItem {
  id: number
  username: string
  email: string
}
const supportConfig = ref<SupportConfigItem>({
  id: 0,
  support_user: null,
  support_username: '',
  support_email: '',
  institutions_assigned: 0,
})
const supportUsers = ref<SupportUserItem[]>([])
const supportCreateForm = reactive({ email: '', password: '' })
const creatingSupportUser = ref(false)
const assigningSupport = ref(false)

// Products (points catalog)
interface ProductCategoryItem {
  id: number
  name: string
  slug: string
  sort_order: number
  is_active: boolean
  product_count?: number
}
interface ProductItem {
  id: number
  category: number | null
  category_name?: string | null
  name: string
  description: string
  price_in_points: string
  is_active: boolean
  image_url?: string | null
  created_at: string
}
const productCategories = ref<ProductCategoryItem[]>([])
const loadingCategories = ref(false)
const categoryDialog = ref(false)
const editingCategory = ref<ProductCategoryItem | null>(null)
const savingCategory = ref(false)
const deleteCategoryDialog = ref(false)
const categoryToDelete = ref<ProductCategoryItem | null>(null)
const deletingCategory = ref(false)
const categoryHeaders = [
  { title: 'Название', key: 'name' },
  { title: 'Slug', key: 'slug' },
  { title: 'Порядок', key: 'sort_order', width: '90' },
  { title: 'Товаров', key: 'product_count', width: '90' },
  { title: 'Активна', key: 'is_active', width: '100' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]
const categoryForm = reactive({
  name: '',
  slug: '',
  sort_order: 0,
  is_active: true,
})
const products = ref<ProductItem[]>([])
const loadingProducts = ref(false)
const productDialog = ref(false)
const editingProduct = ref<ProductItem | null>(null)
const savingProduct = ref(false)
const deleteProductDialog = ref(false)
const productToDelete = ref<ProductItem | null>(null)
const deletingProduct = ref(false)
const categorySelectItems = computed(() =>
  productCategories.value.map((c) => ({ title: c.name, value: c.id }))
)
const productHeaders = [
  { title: 'Фото', key: 'image_url', sortable: false, width: '70' },
  { title: 'Название', key: 'name' },
  { title: 'Категория', key: 'category_name' },
  { title: 'Цена', key: 'price_in_points' },
  { title: 'Активен', key: 'is_active', width: '100' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]
const productForm = reactive({
  category: null as number | null,
  name: '',
  description: '',
  price_in_points: 0,
  is_active: true,
  imageFile: null as File | File[] | null,
  imagePreview: '' as string,
})

// Points orders (admin)
interface PointsOrderLineItem {
  id: number
  product: number
  product_name: string
  quantity: number
  price_at_order: string
}
interface PointsOrderItem {
  id: number
  institution: number
  institution_name: string
  status: string
  recipient_name: string
  recipient_phone: string
  address: string
  total_points: string
  created_at: string
  lines: PointsOrderLineItem[]
}
const pointsOrders = ref<PointsOrderItem[]>([])
const loadingPointsOrders = ref(false)
const pointsOrderStatusFilter = ref('all')
const pointsOrderStatusOptions = [
  { title: 'Все', value: 'all' },
  { title: 'Ожидает', value: 'pending' },
  { title: 'Принят', value: 'accepted' },
  { title: 'Доставлен', value: 'completed' },
  { title: 'Отменён', value: 'cancelled' },
]
const pointsOrderHeaders = [
  { title: 'ID', key: 'id', width: '70' },
  { title: 'Организация', key: 'institution_name' },
  { title: 'Получатель', key: 'recipient_name' },
  { title: 'Телефон', key: 'recipient_phone', width: '130' },
  { title: 'Сумма', key: 'total_points', width: '100' },
  { title: 'Статус', key: 'status', width: '110' },
  { title: 'Дата', key: 'created_at', width: '110' },
  { title: 'Действия', key: 'actions', sortable: false, width: '100' },
]
const selectedPointsOrder = ref<PointsOrderItem | null>(null)
const pointsOrderDetailDialog = ref(false)
const pointsOrderStatusEdit = ref('pending')
const savingPointsOrderStatus = ref(false)

const filteredPointsOrders = computed(() => {
  if (pointsOrderStatusFilter.value === 'all') return pointsOrders.value
  return pointsOrders.value.filter((o) => o.status === pointsOrderStatusFilter.value)
})

const filteredBonuses = computed(() => {
  if (bonusStatusFilter.value === 'all') return institutionBonuses.value
  return institutionBonuses.value.filter((b) => b.status === bonusStatusFilter.value)
})

const filteredInstitutions = computed(() => {
  const q = institutionSearchName.value?.trim().toLowerCase() || ''
  if (!q) return institutions.value
  return institutions.value.filter((i) => i.institution_name.toLowerCase().includes(q))
})

function startOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}

function endOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999)
}

function parseCreatedAt(createdAt: string) {
  if (!createdAt) return null
  const d = new Date(createdAt)
  return Number.isNaN(d.getTime()) ? null : d
}

function isRequestInDateRange(createdAt: string, from: Date, to: Date) {
  const d = parseCreatedAt(createdAt)
  if (!d) return false
  return d >= from && d <= to
}

function getRequestDateFilterRange(): { from: Date; to: Date } | null {
  const now = new Date()
  const to = endOfDay(now)

  switch (requestDateFilter.value) {
    case 'all':
      return null
    case 'today':
      return { from: startOfDay(now), to }
    case 'yesterday': {
      const day = new Date(now)
      day.setDate(day.getDate() - 1)
      return { from: startOfDay(day), to: endOfDay(day) }
    }
    case 'week': {
      const from = new Date(now)
      const weekday = from.getDay()
      const daysFromMonday = weekday === 0 ? 6 : weekday - 1
      from.setDate(from.getDate() - daysFromMonday)
      return { from: startOfDay(from), to }
    }
    case 'month':
      return { from: startOfDay(new Date(now.getFullYear(), now.getMonth(), 1)), to }
    case 'quarter': {
      const quarterMonth = Math.floor(now.getMonth() / 3) * 3
      return { from: startOfDay(new Date(now.getFullYear(), quarterMonth, 1)), to }
    }
    case 'half_year': {
      const halfMonth = now.getMonth() < 6 ? 0 : 6
      return { from: startOfDay(new Date(now.getFullYear(), halfMonth, 1)), to }
    }
    case 'year':
      return { from: startOfDay(new Date(now.getFullYear(), 0, 1)), to }
    case 'range': {
      if (!requestDateFrom.value && !requestDateTo.value) return null
      const rawFrom = requestDateFrom.value
        ? startOfDay(new Date(`${requestDateFrom.value}T00:00:00`))
        : new Date(0)
      const rawTo = requestDateTo.value
        ? endOfDay(new Date(`${requestDateTo.value}T00:00:00`))
        : to
      if (rawFrom > rawTo) {
        return {
          from: requestDateTo.value
            ? startOfDay(new Date(`${requestDateTo.value}T00:00:00`))
            : new Date(0),
          to: requestDateFrom.value
            ? endOfDay(new Date(`${requestDateFrom.value}T00:00:00`))
            : to,
        }
      }
      return { from: rawFrom, to: rawTo }
    }
    default:
      return null
  }
}

const filteredAdminRequests = computed(() => {
  let list = adminRequests.value
  if (requestStatusFilter.value !== 'all') {
    list = list.filter((r) => r.status === requestStatusFilter.value)
  }
  const dateRange = getRequestDateFilterRange()
  if (dateRange) {
    list = list.filter((r) => isRequestInDateRange(r.created_at, dateRange.from, dateRange.to))
  }
  const instQ = requestInstitutionFilter.value?.trim().toLowerCase() || ''
  if (instQ) {
    list = list.filter((r) => (r.institution_name || '').toLowerCase().includes(instQ))
  }
  const compQ = requestCompanyFilter.value?.trim().toLowerCase() || ''
  if (compQ) {
    list = list.filter((r) => (r.receiving_company_name || '').toLowerCase().includes(compQ))
  }
  return list
})

function openInstitutionCard(item: InstitutionProfile) {
  institutionCard.value = item
  institutionCardDialog.value = true
}

function openRequestCard(item: CollectionRequest) {
  requestCard.value = item
  requestCardDialog.value = true
}

function openInstitutionRegistrationCard(item: InstitutionRegistrationRequest) {
  institutionRegistrationCard.value = item
  institutionRegistrationCardDialog.value = true
}

function openCompanyRegistrationCard(item: CompanyRegistrationRequest) {
  companyRegistrationCard.value = item
  companyRegistrationCardDialog.value = true
}

function requestStatusLabel(s: string) {
  const m: Record<string, string> = {
    new: 'Новый',
    accepted: 'Принят',
    pending_confirmation: 'Ожидает подтверждения',
    completed: 'Завершён',
    cancelled: 'Отменён',
  }
  return m[s] || s
}

function requestStatusColor(s: string) {
  const m: Record<string, string> = {
    new: 'warning',
    accepted: 'info',
    pending_confirmation: 'warning',
    completed: 'success',
    cancelled: 'grey',
  }
  return m[s] || 'default'
}

async function loadPrices() {
  loadingPrices.value = true
  try {
    const { data } = await api.get<PriceList[]>('/prices/')
    prices.value = data
  } finally {
    loadingPrices.value = false
  }
}

async function loadMaterials() {
  loadingMaterials.value = true
  try {
    const { data } = await api.get<Material[]>('/materials/')
    materials.value = data
  } finally {
    loadingMaterials.value = false
  }
}

async function loadCompanies() {
  loadingCompanies.value = true
  try {
    const { data } = await api.get<CompanyProfile[]>('/company-profiles/')
    companies.value = data
  } finally {
    loadingCompanies.value = false
  }
}

async function loadInstitutions() {
  loadingInstitutions.value = true
  try {
    const { data } = await api.get<InstitutionProfile[]>('/institutions/')
    institutions.value = data
  } finally {
    loadingInstitutions.value = false
  }
}

async function loadRequests() {
  loadingRequests.value = true
  try {
    const { data } = await api.get<CollectionRequest[]>('/collection-requests/')
    adminRequests.value = data
  } finally {
    loadingRequests.value = false
  }
}

function formatDate(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatDateOnly(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

async function loadPickupRequests() {
  loadingPickupRequests.value = true
  try {
    const { data } = await api.get<PublicPickupRequest[]>('/public/pickup-requests/')
    pickupRequests.value = Array.isArray(data) ? data : []
  } catch {
    pickupRequests.value = []
  } finally {
    loadingPickupRequests.value = false
  }
}

async function updatePickupStatus(item: PublicPickupRequest, status: PublicPickupStatus) {
  try {
    await api.patch(`/public/pickup-requests/${item.id}/`, { status })
    item.status = status
    const opt = pickupStatusOptions.find((o) => o.value === status)
    if (opt) item.status_display = opt.title
    if (pickupRequestCard.value?.id === item.id) {
      pickupRequestCard.value.status = status
      if (opt) pickupRequestCard.value.status_display = opt.title
    }
  } catch {
    showSnackbar('Не удалось обновить статус', 'error')
  }
}

function pickupStatusLabel(status: PublicPickupStatus) {
  return pickupStatusOptions.find((o) => o.value === status)?.title || status
}

function openPickupRequestCard(item: PublicPickupRequest) {
  pickupRequestCard.value = item
  pickupRequestCardDialog.value = true
}

function openPickupNotes(item: PublicPickupRequest) {
  pickupNotesTarget.value = item
  pickupNotesForm.value = item.admin_notes || ''
  pickupNotesDialog.value = true
}

async function savePickupNotes() {
  if (!pickupNotesTarget.value) return
  savingPickupNotes.value = true
  try {
    await api.patch(`/public/pickup-requests/${pickupNotesTarget.value.id}/`, {
      admin_notes: pickupNotesForm.value,
    })
    pickupNotesTarget.value.admin_notes = pickupNotesForm.value
    if (pickupRequestCard.value?.id === pickupNotesTarget.value.id) {
      pickupRequestCard.value.admin_notes = pickupNotesForm.value
    }
    pickupNotesDialog.value = false
    showSnackbar('Сохранено', 'success')
  } catch {
    showSnackbar('Ошибка сохранения', 'error')
  } finally {
    savingPickupNotes.value = false
  }
}

async function loadRegistrationRequests() {
  loadingRegistrationRequests.value = true
  try {
    const { data } = await api.get<InstitutionRegistrationRequest[]>('/registration-requests/')
    registrationRequests.value = Array.isArray(data) ? data : []
  } catch {
    registrationRequests.value = []
  } finally {
    loadingRegistrationRequests.value = false
  }
}

async function loadCompanyRegistrationRequests() {
  loadingCompanyRegistrationRequests.value = true
  try {
    const { data } = await api.get<CompanyRegistrationRequest[]>('/company-registration-requests/')
    companyRegistrationRequests.value = Array.isArray(data) ? data : []
  } catch {
    companyRegistrationRequests.value = []
  } finally {
    loadingCompanyRegistrationRequests.value = false
  }
}

function auditCategoryColor(category: string) {
  if (category === 'critical') return 'error'
  if (category === 'warning') return 'warning'
  return 'info'
}

async function loadAuditLogs() {
  loadingAuditLogs.value = true
  try {
    const { data } = await api.get<AuditLogsResponse>('/audit-logs/', {
      params: {
        page: auditPage.value,
        page_size: auditPageSize.value,
        category: auditCategoryFilter.value !== 'all' ? auditCategoryFilter.value : undefined,
        actor_role: auditRoleFilter.value !== 'all' ? auditRoleFilter.value : undefined,
        search: auditSearch.value || undefined,
      },
    })
    auditLogs.value = Array.isArray(data?.results) ? data.results : []
    auditTotal.value = Number(data?.count || 0)
  } catch {
    auditLogs.value = []
    auditTotal.value = 0
  } finally {
    loadingAuditLogs.value = false
  }
}

async function exportAuditLogs(format: 'csv' | 'txt') {
  try {
    const response = await api.get('/audit-logs/export/', {
      params: {
        export_format: format,
        category: auditCategoryFilter.value !== 'all' ? auditCategoryFilter.value : undefined,
        actor_role: auditRoleFilter.value !== 'all' ? auditRoleFilter.value : undefined,
        search: auditSearch.value || undefined,
      },
      responseType: 'blob',
    })
    const blob = new Blob([response.data], { type: format === 'txt' ? 'text/plain' : 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `audit_logs.${format}`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch {
    snackbar.value = { show: true, text: 'Не удалось экспортировать логи', color: 'error' }
  }
}

async function loadDatabaseInfo() {
  databaseInfoError.value = ''
  try {
    const { data } = await api.get<DatabaseInfo>('/database-info/')
    databaseInfo.value = data
  } catch {
    databaseInfo.value = null
    databaseInfoError.value = 'Не удалось загрузить информацию о базе данных'
  }
}

async function fetchBonusConfig() {
  try {
    const { data } = await api.get<{ bonus_percent: string }>('/bonus-config/')
    bonusConfigForm.bonus_percent = parseFloat(data.bonus_percent) || 0
  } catch {
    bonusConfigForm.bonus_percent = 0
  }
}

async function saveBonusConfig() {
  savingBonusConfig.value = true
  try {
    await api.patch('/bonus-config/', { bonus_percent: bonusConfigForm.bonus_percent })
    showSnackbar('Процент бонуса сохранён', 'success')
  } catch (e: unknown) {
    showSnackbar((e as { response?: { data?: { bonus_percent?: string[] } } })?.response?.data?.bonus_percent?.[0] || 'Ошибка сохранения', 'error')
  } finally {
    savingBonusConfig.value = false
  }
}

async function fetchInstitutionBonuses() {
  loadingBonuses.value = true
  try {
    const params = bonusStatusFilter.value !== 'all' ? { status: bonusStatusFilter.value } : {}
    const { data } = await api.get<InstitutionBonusItem[]>('/institution-bonuses/', { params })
    institutionBonuses.value = Array.isArray(data) ? data : []
  } catch {
    institutionBonuses.value = []
  } finally {
    loadingBonuses.value = false
  }
}

function openBonusAwardDialog(item: InstitutionBonusItem) {
  editingBonus.value = item
  bonusAwardForm.awarded_amount = parseFloat(item.awarded_amount ?? item.calculated_amount) || 0
  bonusAwardDialog.value = true
}

async function fetchSupportConfig() {
  try {
    const { data } = await api.get<SupportConfigItem>('/support-config/')
    supportConfig.value = data
  } catch {
    supportConfig.value = {
      id: 0,
      support_user: null,
      support_username: '',
      support_email: '',
      institutions_assigned: 0,
    }
  }
}

async function fetchSupportUsers() {
  try {
    const { data } = await api.get<SupportUserItem[]>('/support-users/')
    supportUsers.value = Array.isArray(data) ? data : []
  } catch {
    supportUsers.value = []
  }
}

async function createSupportUser() {
  const email = supportCreateForm.email.trim()
  if (!email) {
    showSnackbar('Укажите email', 'error')
    return
  }
  creatingSupportUser.value = true
  try {
    const payload: { email: string; password?: string } = { email }
    if (supportCreateForm.password.trim()) {
      payload.password = supportCreateForm.password
    }
    await api.post('/support-users/', payload)
    showSnackbar('Аккаунт техподдержки создан и назначен на все учреждения', 'success')
    supportCreateForm.email = ''
    supportCreateForm.password = ''
    await Promise.all([fetchSupportUsers(), fetchSupportConfig()])
  } catch (e: unknown) {
    const err = e as { response?: { data?: { email?: string[]; detail?: string } } }
    showSnackbar(err.response?.data?.email?.[0] || err.response?.data?.detail || 'Ошибка создания', 'error')
  } finally {
    creatingSupportUser.value = false
  }
}

async function assignSupportToAll() {
  const userId = supportConfig.value.support_user ?? supportUsers.value[0]?.id
  if (!userId) {
    showSnackbar('Сначала создайте аккаунт техподдержки', 'error')
    return
  }
  assigningSupport.value = true
  try {
    const { data } = await api.patch<SupportConfigItem>('/support-config/', { support_user: userId })
    supportConfig.value = data
    showSnackbar(`Специалист назначен на ${data.institutions_assigned} учреждений`, 'success')
  } catch {
    showSnackbar('Не удалось назначить специалиста', 'error')
  } finally {
    assigningSupport.value = false
  }
}

async function confirmBonusAward() {
  if (!editingBonus.value) return
  savingBonusAward.value = true
  try {
    await api.patch(`/institution-bonuses/${editingBonus.value.id}/`, {
      awarded_amount: bonusAwardForm.awarded_amount,
      status: 'confirmed',
    })
    showSnackbar('Бонус начислен', 'success')
    bonusAwardDialog.value = false
    editingBonus.value = null
    await fetchInstitutionBonuses()
  } catch (e: unknown) {
    showSnackbar((e as { response?: { data?: Record<string, unknown> } })?.response?.data ? JSON.stringify((e as { response: { data: Record<string, unknown> } }).response.data) : 'Ошибка', 'error')
  } finally {
    savingBonusAward.value = false
  }
}

async function loadProductCategories() {
  loadingCategories.value = true
  try {
    const { data } = await api.get<ProductCategoryItem[]>('/product-categories/')
    productCategories.value = data
  } catch {
    productCategories.value = []
  } finally {
    loadingCategories.value = false
  }
}

function slugifyCategoryName(name: string) {
  return name
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9\u0400-\u04FF-]/g, '')
}

function openCategoryDialog(item?: ProductCategoryItem) {
  editingCategory.value = item ?? null
  if (item) {
    categoryForm.name = item.name
    categoryForm.slug = item.slug
    categoryForm.sort_order = item.sort_order
    categoryForm.is_active = item.is_active
  } else {
    categoryForm.name = ''
    categoryForm.slug = ''
    categoryForm.sort_order = (productCategories.value.length + 1) * 10
    categoryForm.is_active = true
  }
  categoryDialog.value = true
}

async function saveCategory() {
  savingCategory.value = true
  try {
    const payload = {
      name: categoryForm.name,
      slug: categoryForm.slug || slugifyCategoryName(categoryForm.name),
      sort_order: categoryForm.sort_order,
      is_active: categoryForm.is_active,
    }
    if (editingCategory.value) {
      await api.patch(`/product-categories/${editingCategory.value.id}/`, payload)
    } else {
      await api.post('/product-categories/', payload)
    }
    showSnackbar('Категория сохранена', 'success')
    categoryDialog.value = false
    await loadProductCategories()
  } catch {
    showSnackbar('Ошибка сохранения категории', 'error')
  } finally {
    savingCategory.value = false
  }
}

function confirmDeleteCategory(item: ProductCategoryItem) {
  categoryToDelete.value = item
  deleteCategoryDialog.value = true
}

async function doDeleteCategory() {
  if (!categoryToDelete.value) return
  deletingCategory.value = true
  try {
    await api.delete(`/product-categories/${categoryToDelete.value.id}/`)
    showSnackbar('Категория удалена', 'success')
    deleteCategoryDialog.value = false
    categoryToDelete.value = null
    await loadProductCategories()
    await loadProducts()
  } catch {
    showSnackbar('Ошибка удаления', 'error')
  } finally {
    deletingCategory.value = false
  }
}

async function loadProducts() {
  loadingProducts.value = true
  try {
    const { data } = await api.get<ProductItem[]>('/products/')
    products.value = data
  } catch {
    products.value = []
  } finally {
    loadingProducts.value = false
  }
}

function openProductDialog(item?: ProductItem) {
  editingProduct.value = item ?? null
  productForm.imageFile = null
  productForm.imagePreview = ''
  if (item) {
    productForm.category = item.category
    productForm.name = item.name
    productForm.description = item.description || ''
    productForm.price_in_points = parseFloat(item.price_in_points) || 0
    productForm.is_active = item.is_active
    if (item.image_url) productForm.imagePreview = resolveMediaUrl(item.image_url)
  } else {
    productForm.category = null
    productForm.name = ''
    productForm.description = ''
    productForm.price_in_points = 0
    productForm.is_active = true
  }
  productDialog.value = true
}

async function saveProduct() {
  savingProduct.value = true
  try {
    const file = pickFirstFile(productForm.imageFile)
    if (file) {
      const formData = new FormData()
      formData.append('name', productForm.name)
      formData.append('description', productForm.description)
      formData.append('price_in_points', String(productForm.price_in_points))
      formData.append('is_active', productForm.is_active ? 'true' : 'false')
      if (productForm.category) formData.append('category', String(productForm.category))
      formData.append('image', file)
      // Do not set Content-Type: axios must set multipart/form-data with boundary so the server receives the file
      if (editingProduct.value) {
        await api.patch(`/products/${editingProduct.value.id}/`, formData)
      } else {
        await api.post('/products/', formData)
      }
    } else {
      const payload = {
        category: productForm.category,
        name: productForm.name,
        description: productForm.description,
        price_in_points: productForm.price_in_points,
        is_active: productForm.is_active,
      }
      if (editingProduct.value) {
        await api.patch(`/products/${editingProduct.value.id}/`, payload)
      } else {
        await api.post('/products/', payload)
      }
    }
    showSnackbar('Сохранено', 'success')
    productDialog.value = false
    await loadProducts()
  } catch {
    showSnackbar('Ошибка сохранения', 'error')
  } finally {
    savingProduct.value = false
  }
}

function confirmDeleteProduct(item: ProductItem) {
  productToDelete.value = item
  deleteProductDialog.value = true
}

async function doDeleteProduct() {
  if (!productToDelete.value) return
  deletingProduct.value = true
  try {
    await api.delete(`/products/${productToDelete.value.id}/`)
    showSnackbar('Товар удалён', 'success')
    deleteProductDialog.value = false
    productToDelete.value = null
    await loadProducts()
  } catch {
    showSnackbar('Ошибка удаления', 'error')
  } finally {
    deletingProduct.value = false
  }
}

async function loadPointsOrders() {
  loadingPointsOrders.value = true
  try {
    const { data } = await api.get<PointsOrderItem[]>('/points-orders/')
    pointsOrders.value = Array.isArray(data) ? data : []
  } catch {
    pointsOrders.value = []
  } finally {
    loadingPointsOrders.value = false
  }
}

function openPointsOrderDetail(order: PointsOrderItem) {
  selectedPointsOrder.value = order
  pointsOrderStatusEdit.value = order.status
  pointsOrderDetailDialog.value = true
}

function pointsOrderStatusLabel(s: string) {
  const m: Record<string, string> = { pending: 'Ожидает', accepted: 'Принят', completed: 'Доставлен', cancelled: 'Отменён' }
  return m[s] || s
}

function pointsOrderStatusColor(s: string) {
  const m: Record<string, string> = { pending: 'warning', accepted: 'info', completed: 'success', cancelled: 'default' }
  return m[s] || 'default'
}

async function savePointsOrderStatus() {
  if (!selectedPointsOrder.value) return
  savingPointsOrderStatus.value = true
  try {
    await api.patch(`/points-orders/${selectedPointsOrder.value.id}/`, { status: pointsOrderStatusEdit.value })
    selectedPointsOrder.value.status = pointsOrderStatusEdit.value
    showSnackbar('Статус сохранён', 'success')
  } catch {
    showSnackbar('Ошибка сохранения статуса', 'error')
  } finally {
    savingPointsOrderStatus.value = false
  }
}

async function loadNews() {
  loadingNews.value = true
  try {
    const { data } = await api.get<NewsArticle[]>('/news/')
    newsArticles.value = Array.isArray(data) ? data : []
  } finally {
    loadingNews.value = false
  }
}

function formatNewsDate(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function openNewsDialog(item?: NewsArticle) {
  editingNews.value = item ?? null
  if (item) {
    newsForm.title = item.title
    newsForm.content = item.content
    newsForm.is_published = item.is_published
    newsForm.imageFile = null
    newsForm.imagePreview = item.image_url || ''
  } else {
    newsForm.title = ''
    newsForm.content = ''
    newsForm.is_published = true
    newsForm.imageFile = null
    newsForm.imagePreview = ''
  }
  newsDialog.value = true
}

function onNewsImageChange(files: File[] | File | null) {
  const arr = Array.isArray(files) ? files : files ? [files] : []
  if (arr.length > 0) {
    newsForm.imagePreview = URL.createObjectURL(arr[0])
  } else {
    newsForm.imagePreview = ''
  }
}

async function saveNews() {
  savingNews.value = true
  try {
    const formData = new FormData()
    formData.append('title', newsForm.title)
    formData.append('content', newsForm.content)
    formData.append('is_published', String(newsForm.is_published))
    const newsImage = pickFirstFile(newsForm.imageFile)
    if (newsImage) {
      formData.append('image', newsImage)
    }
    if (editingNews.value) {
      await api.patch(`/news/${editingNews.value.id}/`, formData)
    } else {
      await api.post('/news/', formData)
    }
    newsDialog.value = false
    await loadNews()
  } finally {
    savingNews.value = false
  }
}

function confirmDeleteNews(item: NewsArticle) {
  newsToDelete.value = item
  deleteNewsDialog.value = true
}

async function doDeleteNews() {
  if (!newsToDelete.value) return
  deletingNews.value = true
  try {
    await api.delete(`/news/${newsToDelete.value.id}/`)
    deleteNewsDialog.value = false
    newsToDelete.value = null
    await loadNews()
  } finally {
    deletingNews.value = false
  }
}

async function toggleNewsPublish(item: NewsArticle) {
  try {
    await api.patch(`/news/${item.id}/`, { is_published: !item.is_published })
    await loadNews()
  } catch {
    // ignore
  }
}

function openPriceDialog(item?: PriceList) {
  editingPrice.value = item ?? null
  priceFormError.value = ''
  priceFormErrors.value = {}
  if (item) {
    priceForm.material = item.material
    priceForm.price_per_kg = String(item.price_per_kg)
    priceForm.is_active = item.is_active
  } else {
    priceForm.material = availableMaterialsForPrice.value[0]?.id ?? null
    priceForm.price_per_kg = ''
    priceForm.is_active = true
  }
  priceDialog.value = true
}

function openMaterialDialog(item?: Material) {
  editingMaterial.value = item ?? null
  materialFormErrors.value = {}
  materialForm.iconImageFile = null
  materialForm.imageFile = null
  materialForm.iconPreview = ''
  materialForm.imagePreview = ''
  materialForm.clearIconImage = false
  materialForm.clearImage = false
  if (item) {
    materialForm.name = item.name
    materialForm.code = item.code
    materialForm.short_description = item.short_description || ''
    materialForm.icon = item.icon || ''
    materialForm.sort_order = item.sort_order ?? 0
    materialForm.is_active = item.is_active
    if (item.icon_url) materialForm.iconPreview = resolveMediaUrl(item.icon_url)
    if (item.image_url) materialForm.imagePreview = resolveMediaUrl(item.image_url)
  } else {
    materialForm.name = ''
    materialForm.code = ''
    materialForm.short_description = ''
    materialForm.icon = ''
    materialForm.sort_order = 0
    materialForm.is_active = true
  }
  materialDialog.value = true
}

function onClearMaterialIcon() {
  materialForm.iconImageFile = null
  materialForm.iconPreview = ''
  if (editingMaterial.value?.icon_url) materialForm.clearIconImage = true
}

function onClearMaterialPhoto() {
  materialForm.imageFile = null
  materialForm.imagePreview = ''
  if (editingMaterial.value?.image_url) materialForm.clearImage = true
}

function appendMaterialFormData(formData: FormData, name: string, code: string) {
  formData.append('name', name)
  if (!editingMaterial.value) formData.append('code', code)
  formData.append('short_description', materialForm.short_description)
  formData.append('icon', materialForm.icon)
  formData.append('sort_order', String(materialForm.sort_order))
  formData.append('is_active', String(materialForm.is_active))
  const iconFile = pickFirstFile(materialForm.iconImageFile)
  const imageFile = pickFirstFile(materialForm.imageFile)
  if (iconFile) formData.append('icon_image', iconFile)
  if (imageFile) formData.append('image', imageFile)
  if (materialForm.clearIconImage) formData.append('clear_icon_image', 'true')
  if (materialForm.clearImage) formData.append('clear_image', 'true')
}

async function saveMaterial() {
  materialFormErrors.value = {}
  const name = (materialForm.name || '').trim()
  const code = (materialForm.code || '').trim().toLowerCase()
  if (!name) {
    materialFormErrors.value.name = 'Введите название'
    return
  }
  if (!editingMaterial.value && !code) {
    materialFormErrors.value.code = 'Введите код (латиница)'
    return
  }
  savingMaterial.value = true
  try {
    const iconFile = pickFirstFile(materialForm.iconImageFile)
    const imageFile = pickFirstFile(materialForm.imageFile)
    const hasUploads = !!(iconFile || imageFile || materialForm.clearIconImage || materialForm.clearImage)
    if (hasUploads) {
      const formData = new FormData()
      appendMaterialFormData(formData, name, code)
      if (editingMaterial.value) {
        await api.patch(`/materials/${editingMaterial.value.id}/`, formData)
      } else {
        await api.post('/materials/', formData)
      }
    } else {
      const payload = {
        name,
        short_description: materialForm.short_description,
        icon: materialForm.icon,
        sort_order: materialForm.sort_order,
        is_active: materialForm.is_active,
        ...(editingMaterial.value ? {} : { code }),
      }
      if (editingMaterial.value) {
        await api.patch(`/materials/${editingMaterial.value.id}/`, payload)
      } else {
        await api.post('/materials/', payload)
      }
    }
    materialDialog.value = false
    await loadMaterials()
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, string | string[]> } }
    const d = ax.response?.data
    if (d) {
      if (d.name) materialFormErrors.value.name = Array.isArray(d.name) ? d.name.join(' ') : d.name
      if (d.code) materialFormErrors.value.code = Array.isArray(d.code) ? d.code.join(' ') : d.code
      else if (d.detail) materialFormErrors.value.code = typeof d.detail === 'string' ? d.detail : String(d.detail)
    }
  } finally {
    savingMaterial.value = false
  }
}

async function savePrice() {
  priceFormError.value = ''
  priceFormErrors.value = {}
  if (!editingPrice.value && (priceForm.material == null || priceForm.material === '')) {
    priceFormError.value = 'Выберите материал'
    return
  }
  const priceNum = Number(priceForm.price_per_kg)
  if (!editingPrice.value && (priceForm.price_per_kg === '' || isNaN(priceNum) || priceNum < 0)) {
    priceFormErrors.value.price_per_kg = 'Введите число не меньше 0'
    return
  }
  if (editingPrice.value && (isNaN(priceNum) || priceNum < 0)) {
    priceFormErrors.value.price_per_kg = 'Введите число не меньше 0'
    return
  }
  savingPrice.value = true
  try {
    if (editingPrice.value) {
      await api.patch(`/prices/${editingPrice.value.id}/`, {
        price_per_kg: String(priceForm.price_per_kg),
        is_active: priceForm.is_active,
      })
    } else {
      await api.post('/prices/', {
        material: priceForm.material,
        price_per_kg: String(priceForm.price_per_kg),
        is_active: priceForm.is_active,
      })
    }
    priceDialog.value = false
    await loadPrices()
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, string | string[]> } }
    const d = ax.response?.data
    if (d) {
      if (typeof d.material === 'string') priceFormError.value = d.material
      else if (Array.isArray(d.material)) priceFormError.value = d.material.join(' ')
      else if (d.price_per_kg) priceFormErrors.value.price_per_kg = Array.isArray(d.price_per_kg) ? d.price_per_kg.join(' ') : d.price_per_kg
      else if (d.detail) priceFormError.value = typeof d.detail === 'string' ? d.detail : String(d.detail)
      else priceFormError.value = Object.values(d).flat().join(' ')
    } else {
      priceFormError.value = 'Не удалось сохранить'
    }
  } finally {
    savingPrice.value = false
  }
}

async function togglePriceActive(item: PriceList) {
  try {
    await api.patch(`/prices/${item.id}/`, { is_active: !item.is_active })
    await loadPrices()
  } catch {
    // snackbar or ignore
  }
}

function openCompanyCard(item: CompanyProfile) {
  companyCard.value = item
  companyCardDialog.value = true
}

function openCompanyDialog(item?: CompanyProfile) {
  companyFormErrors.value = {}
  editingCompany.value = item ?? null
  if (item) {
    companyForm.company_name = item.company_name
    companyForm.contact_email = item.contact_email
    companyForm.contact_phone = item.contact_phone
    companyForm.address = item.address ?? ''
    companyForm.legal_address = item.legal_address ?? ''
    companyForm.inn = item.inn ?? ''
    companyForm.kpp = item.kpp ?? ''
    companyForm.ogrn = item.ogrn ?? ''
    companyForm.bank_account = item.bank_account ?? ''
    companyForm.bank_name = item.bank_name ?? ''
    companyForm.bik = item.bik ?? ''
    companyForm.corr_account = item.corr_account ?? ''
    companyForm.website = item.website ?? ''
    companyForm.description = item.description ?? ''
  } else {
    companyForm.company_name = ''
    companyForm.contact_email = ''
    companyForm.password = ''
    companyForm.contact_phone = ''
    companyForm.address = ''
    companyForm.legal_address = ''
    companyForm.inn = ''
    companyForm.kpp = ''
    companyForm.ogrn = ''
    companyForm.bank_account = ''
    companyForm.bank_name = ''
    companyForm.bik = ''
    companyForm.corr_account = ''
    companyForm.website = ''
    companyForm.description = ''
  }
  companyDialog.value = true
}

async function saveCompany() {
  companyFormErrors.value = {}
  savingCompany.value = true
  try {
    const payload: Record<string, string> = {
      company_name: companyForm.company_name,
      contact_phone: companyForm.contact_phone,
      address: companyForm.address,
      contact_email: companyForm.contact_email,
      legal_address: companyForm.legal_address || '',
      inn: companyForm.inn || '',
      kpp: companyForm.kpp || '',
      ogrn: companyForm.ogrn || '',
      bank_account: companyForm.bank_account || '',
      bank_name: companyForm.bank_name || '',
      bik: companyForm.bik || '',
      corr_account: companyForm.corr_account || '',
      website: companyForm.website || '',
      description: companyForm.description || '',
    }
    if (editingCompany.value) {
      if (companyForm.password) payload.password = companyForm.password
      await api.patch(`/company-profiles/${editingCompany.value.id}/`, payload)
    } else {
      await api.post('/company-profiles/', {
        ...payload,
        email: companyForm.contact_email,
        password: companyForm.password || undefined,
      })
    }
    companyDialog.value = false
    await loadCompanies()
    snackbar.value = { show: true, text: 'Сохранено', color: 'success' }
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, unknown>; status?: number } }
    const data = ax.response?.data
    if (ax.response?.status === 400 && data && typeof data === 'object') {
      const errors: Record<string, string[]> = {}
      for (const [k, v] of Object.entries(data)) {
        errors[k] = Array.isArray(v) ? v.map(String) : [String(v)]
      }
      companyFormErrors.value = errors
      snackbar.value = { show: true, text: 'Исправьте ошибки в форме', color: 'error' }
    } else {
      snackbar.value = { show: true, text: (data && typeof (data as { detail?: string }).detail === 'string') ? (data as { detail: string }).detail : 'Ошибка при сохранении', color: 'error' }
    }
  } finally {
    savingCompany.value = false
  }
}

function confirmDeleteCompany(item: CompanyProfile) {
  companyToDelete.value = item
  deleteCompanyDialog.value = true
}

async function doDeleteCompany() {
  if (!companyToDelete.value) return
  deletingCompany.value = true
  try {
    await api.delete(`/company-profiles/${companyToDelete.value.id}/`)
    deleteCompanyDialog.value = false
    companyToDelete.value = null
    await loadCompanies()
    await loadInstitutions()
  } finally {
    deletingCompany.value = false
  }
}

async function openInstitutionDialog(item?: InstitutionProfile) {
  institutionFormErrors.value = {}
  editingInstitution.value = item ?? null
  if (item) {
    institutionForm.parent_company = item.parent_company
    institutionForm.email = item.email
    institutionForm.password = ''
    institutionForm.institution_name = item.institution_name
    institutionForm.institution_type = item.institution_type
    institutionForm.address = item.address ?? ''
    institutionForm.contact_person = item.contact_person
    institutionForm.phone = item.phone
    institutionForm.legal_address = item.legal_address ?? ''
    institutionForm.inn = item.inn ?? ''
    institutionForm.kpp = item.kpp ?? ''
    institutionForm.contact_person_on_site = item.contact_person_on_site ?? ''
    institutionForm.phone_on_site = item.phone_on_site ?? ''
    institutionForm.preferred_days = item.preferred_days ?? ''
    institutionForm.preferred_hours = item.preferred_hours ?? ''
    institutionForm.access_details = item.access_details ?? ''
    institutionForm.container_location = item.container_location ?? ''
  } else {
    if (companies.value.length === 0) await loadCompanies()
    institutionForm.parent_company = companies.value.length ? companies.value[0].id : null
    institutionForm.email = ''
    institutionForm.password = ''
    institutionForm.institution_name = ''
    institutionForm.institution_type = ''
    institutionForm.address = ''
    institutionForm.contact_person = ''
    institutionForm.phone = ''
    institutionForm.legal_address = ''
    institutionForm.inn = ''
    institutionForm.kpp = ''
    institutionForm.contact_person_on_site = ''
    institutionForm.phone_on_site = ''
    institutionForm.preferred_days = ''
    institutionForm.preferred_hours = ''
    institutionForm.access_details = ''
    institutionForm.container_location = ''
  }
  institutionDialog.value = true
}

async function saveInstitution() {
  institutionFormErrors.value = {}
  savingInstitution.value = true
  try {
    const payload: Record<string, unknown> = {
      institution_name: institutionForm.institution_name,
      institution_type: institutionForm.institution_type,
      address: institutionForm.address,
      contact_person: institutionForm.contact_person,
      phone: institutionForm.phone,
      email: institutionForm.email,
      legal_address: institutionForm.legal_address || '',
      inn: institutionForm.inn || '',
      kpp: institutionForm.kpp || '',
      contact_person_on_site: institutionForm.contact_person_on_site || '',
      phone_on_site: institutionForm.phone_on_site || '',
      preferred_days: institutionForm.preferred_days || '',
      preferred_hours: institutionForm.preferred_hours || '',
      access_details: institutionForm.access_details || '',
      container_location: institutionForm.container_location || '',
    }
    if (editingInstitution.value) {
      payload.parent_company = institutionForm.parent_company
      if (institutionForm.password) payload.password = institutionForm.password
      await api.patch(`/institutions/${editingInstitution.value.id}/`, payload)
    } else {
      if (institutionForm.parent_company == null) return
      await api.post('/institutions/', {
        ...payload,
        parent_company: institutionForm.parent_company,
        password: institutionForm.password || undefined,
      })
    }
    institutionDialog.value = false
    await loadInstitutions()
    snackbar.value = { show: true, text: 'Сохранено', color: 'success' }
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, unknown>; status?: number } }
    const data = ax.response?.data
    if (ax.response?.status === 400 && data && typeof data === 'object') {
      const errors: Record<string, string[]> = {}
      for (const [k, v] of Object.entries(data)) {
        errors[k] = Array.isArray(v) ? v.map(String) : [String(v)]
      }
      institutionFormErrors.value = errors
      snackbar.value = { show: true, text: 'Исправьте ошибки в форме', color: 'error' }
    } else {
      snackbar.value = { show: true, text: (data && typeof (data as { detail?: string }).detail === 'string') ? (data as { detail: string }).detail : 'Ошибка при сохранении', color: 'error' }
    }
  } finally {
    savingInstitution.value = false
  }
}

function confirmDeleteInstitution(item: InstitutionProfile) {
  institutionToDelete.value = item
  deleteInstitutionDialog.value = true
}

async function doDeleteInstitution() {
  if (!institutionToDelete.value) return
  deletingInstitution.value = true
  try {
    await api.delete(`/institutions/${institutionToDelete.value.id}/`)
    deleteInstitutionDialog.value = false
    institutionToDelete.value = null
    await loadInstitutions()
  } finally {
    deletingInstitution.value = false
  }
}

function logout() {
  authStore.logout()
  userStore.clearUser()
  router.push({ name: 'Login' })
}

watch(activeTab, (tab) => {
  if (tab === 'prices') {
    loadPrices()
    loadMaterials()
  }
  if (tab === 'news') loadNews()
  if (tab === 'companies') loadCompanies()
  if (tab === 'institutions') loadInstitutions()
  if (tab === 'registration-institutions') loadRegistrationRequests()
  if (tab === 'registration-companies') loadCompanyRegistrationRequests()
  if (tab === 'pickup-requests') loadPickupRequests()
  if (tab === 'requests') loadRequests()
  // statistics tab: AdminStatsDashboard loads its own data
  if (tab === 'bonuses') {
    fetchBonusConfig()
    fetchInstitutionBonuses()
  }
  if (tab === 'support') {
    fetchSupportConfig()
    fetchSupportUsers()
  }
  if (tab === 'products') {
    loadProductCategories()
    loadProducts()
  }
  if (tab === 'points-orders') loadPointsOrders()
  if (tab === 'audit-logs') loadAuditLogs()
  if (tab === 'database-info') loadDatabaseInfo()
})

watch([auditCategoryFilter, auditRoleFilter, auditSearch], () => {
  auditPage.value = 1
  if (activeTab.value === 'audit-logs') loadAuditLogs()
})

watch(auditPage, () => {
  if (activeTab.value === 'audit-logs') loadAuditLogs()
})

watch(() => materialForm.iconImageFile, (files) => {
  const file = pickFirstFile(files)
  if (file) {
    materialForm.iconPreview = URL.createObjectURL(file)
    materialForm.clearIconImage = false
  }
})

watch(() => materialForm.imageFile, (files) => {
  const file = pickFirstFile(files)
  if (file) {
    materialForm.imagePreview = URL.createObjectURL(file)
    materialForm.clearImage = false
  }
})

watch(() => productForm.imageFile, (value) => {
  const file = pickFirstFile(value)
  if (file) {
    productForm.imagePreview = URL.createObjectURL(file)
  }
})

onMounted(() => {
  loadPrices()
  loadMaterials()
})
</script>

<style scoped>
.admin-materials-search { min-width: 0; }
.admin-material-thumb { border: 1px solid rgba(0, 0, 0, 0.08); }
.admin-material-preview-box {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  background: #f8fafc;
  overflow: hidden;
}
.admin-material-preview-box--icon {
  width: 96px;
  height: 96px;
  flex-shrink: 0;
}
.admin-material-preview-box--photo {
  width: 140px;
  height: 96px;
  flex-shrink: 0;
}
.admin-material-preview-box__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.admin-reg-detail p {
  margin-bottom: 0.75rem;
  line-height: 1.5;
  word-break: break-word;
}

.admin-reg-detail__link {
  color: var(--vuvoz-primary);
  text-decoration: none;
}
.admin-reg-detail__link:hover {
  text-decoration: underline;
}

.admin-pickup-lines {
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
}
.admin-pickup-lines th,
.admin-pickup-lines td {
  font-size: 0.875rem;
}
@media (max-width: 600px) {
  .admin-materials-table :deep(.v-data-table__td) { padding-left: 8px; padding-right: 8px; }
  .admin-dialog :deep(.v-card) { margin: 8px; max-height: calc(100vh - 16px); }
}
@media (max-width: 960px) {
  .vuvoz-tabs :deep(.v-tab) { min-width: 120px; }
  .v-main .v-container { padding-left: 12px; padding-right: 12px; }
}
</style>
