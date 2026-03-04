<template>
  <div>
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" location="top">
      {{ snackbar.text }}
    </v-snackbar>
    <v-app-bar color="primary" density="compact" class="px-4 py-2">
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
          <v-tab value="registration-requests">Заявки на регистрацию</v-tab>
          <v-tab value="requests">Заявки</v-tab>
          <v-tab value="statistics">Статистика</v-tab>
          <v-tab value="bonuses">Бонусы</v-tab>
          <v-tab value="products">Товары (баллы)</v-tab>
          <v-tab value="points-orders">Заказы на баллы</v-tab>
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
              max-width="440"
              persistent
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

          <!-- Registration requests (from homepage) -->
          <v-window-item value="registration-requests">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Заявки на регистрацию учреждений
                <v-spacer />
                <v-btn variant="outlined" size="small" :loading="loadingRegistrationRequests" @click="loadRegistrationRequests">
                  Обновить
                </v-btn>
              </v-card-title>
              <v-card-text class="text-body-2 text-medium-emphasis">
                Заявки, оставленные через форму «Регистрация» на главной странице. Создайте организацию вручную в разделе «Организации» и привяжите к компании.
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
              </v-data-table>
            </v-card>
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

          <!-- Products (points catalog) -->
          <v-window-item value="products">
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
                <template #item.image_url="{ item }">
                <v-img v-if="item.image_url" :src="item.image_url" width="40" height="40" class="rounded" cover />
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
        </v-window>
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { useBreakpoints } from '@/composables/useBreakpoints'
import type { CompanyProfile, InstitutionProfile, Material, CollectionRequest, NewsArticle, PriceList } from '@/types'
import AdminStatsDashboard from '@/components/admin/AdminStatsDashboard.vue'

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
const materialForm = reactive({ name: '', code: '', is_active: true })
const materialFormErrors = ref<Record<string, string>>({})
const requestStatusFilter = ref('all')

const newsArticles = ref<NewsArticle[]>([])
const loadingNews = ref(false)
const newsDialog = ref(false)
const editingNews = ref<NewsArticle | null>(null)
const savingNews = ref(false)
const newsForm = reactive({
  title: '',
  content: '',
  imageFile: null as File[] | null,
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
interface RegistrationRequestItem {
  id: number
  first_name: string
  patronymic: string
  institution_name: string
  address: string
  phone: string
  created_at: string
}
const registrationRequests = ref<RegistrationRequestItem[]>([])
const loadingRegistrationRequests = ref(false)
const registrationRequestHeaders = [
  { title: 'Учреждение', key: 'institution_name' },
  { title: 'Имя', key: 'first_name' },
  { title: 'Отчество', key: 'patronymic' },
  { title: 'Адрес', key: 'address' },
  { title: 'Телефон', key: 'phone' },
  { title: 'Дата', key: 'created_at', width: '140' },
]

// Admin statistics
interface AdminStatsData {
  materials: { material_type: string; material_type_display: string; total_kg: number; request_count: number }[]
  top_organizations: { institution_id: number; institution_name: string; total_kg: number; request_count: number }[]
  requests_by_status: { status: string; status_display: string; count: number }[]
  weight_over_time: { period_label: string; date_start: string; total_kg: number }[]
}
const adminStats = ref<AdminStatsData | null>(null)
const loadingStats = ref(false)
const statsDateFrom = ref('')
const statsDateTo = ref('')
const statsBasis = ref<'created' | 'completed'>('created')
const statsBasisOptions = [
  { title: 'По дате создания заявки', value: 'created' },
  { title: 'По дате завершения', value: 'completed' },
]
const statsPeriodPreset = ref('year')
const statsPeriodOptions = [
  { title: '1 неделя', value: 'week' },
  { title: '1 месяц', value: 'month' },
  { title: '1 квартал', value: 'quarter' },
  { title: '1 год', value: 'year' },
  { title: 'Свой период', value: 'custom' },
]
const statsEmpty = computed(() => {
  if (!adminStats.value) return true
  const d = adminStats.value
  return (
    d.materials.length === 0 &&
    d.top_organizations.length === 0 &&
    d.requests_by_status.every(s => s.count === 0) &&
    d.weight_over_time.length === 0
  )
})
const statsMaterialFilter = ref('all')
const statsMaterialFilterItems = computed(() => {
  const base = [{ title: 'Все материалы', value: 'all' }]
  const types = adminStats.value?.materials ?? []
  return base.concat(types.map(m => ({ title: m.material_type_display, value: m.material_type })))
})
const filteredMaterials = computed(() => {
  const list = adminStats.value?.materials ?? []
  if (statsMaterialFilter.value === 'all') return list
  return list.filter(m => m.material_type === statsMaterialFilter.value)
})
const viewModeMaterials = ref<'table' | 'graph'>('table')
const viewModeTopOrg = ref<'table' | 'graph'>('table')
const viewModeStatus = ref<'table' | 'graph'>('table')
const viewModeWeight = ref<'table' | 'graph'>('table')
const chartMaterialsRef = ref<HTMLCanvasElement | null>(null)
const chartTopOrgRef = ref<HTMLCanvasElement | null>(null)
const chartStatusRef = ref<HTMLCanvasElement | null>(null)
const chartWeightRef = ref<HTMLCanvasElement | null>(null)
let chartMaterials: Chart | null = null
let chartTopOrg: Chart | null = null
let chartStatus: Chart | null = null
let chartWeight: Chart | null = null
const statsMaterialsHeaders = [
  { title: 'Тип материала', key: 'material_type_display' },
  { title: 'Масса (кг)', key: 'total_kg' },
  { title: 'Кол-во заявок', key: 'request_count' },
]
const statsTopOrgHeaders = [
  { title: 'Организация', key: 'institution_name' },
  { title: 'Масса (кг)', key: 'total_kg' },
  { title: 'Заявок', key: 'request_count' },
]
const statsStatusHeaders = [
  { title: 'Статус', key: 'status_display' },
  { title: 'Количество', key: 'count' },
]
const statsWeightOverTimeHeaders = [
  { title: 'Период', key: 'period_label' },
  { title: 'Масса (кг)', key: 'total_kg' },
]

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

// Products (points catalog)
interface ProductItem {
  id: number
  name: string
  description: string
  price_in_points: string
  is_active: boolean
  image_url?: string | null
  created_at: string
}
const products = ref<ProductItem[]>([])
const loadingProducts = ref(false)
const productDialog = ref(false)
const editingProduct = ref<ProductItem | null>(null)
const savingProduct = ref(false)
const deleteProductDialog = ref(false)
const productToDelete = ref<ProductItem | null>(null)
const deletingProduct = ref(false)
const productHeaders = [
  { title: 'Фото', key: 'image_url', sortable: false, width: '70' },
  { title: 'Название', key: 'name' },
  { title: 'Цена', key: 'price_in_points' },
  { title: 'Активен', key: 'is_active', width: '100' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]
const productForm = reactive({ name: '', description: '', price_in_points: 0, is_active: true, imageFile: null as File[] | null, imagePreview: '' as string })

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

const filteredAdminRequests = computed(() => {
  let list = adminRequests.value
  if (requestStatusFilter.value !== 'all') {
    list = list.filter((r) => r.status === requestStatusFilter.value)
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

function requestStatusLabel(s: string) {
  const m: Record<string, string> = { new: 'Новый', accepted: 'Принят', completed: 'Завершён' }
  return m[s] || s
}

function requestStatusColor(s: string) {
  const m: Record<string, string> = { new: 'warning', accepted: 'info', completed: 'success' }
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

async function loadRegistrationRequests() {
  loadingRegistrationRequests.value = true
  try {
    const { data } = await api.get<RegistrationRequestItem[]>('/registration-requests/')
    registrationRequests.value = Array.isArray(data) ? data : []
  } catch {
    registrationRequests.value = []
  } finally {
    loadingRegistrationRequests.value = false
  }
}

function setStatsDatesFromPreset() {
  const end = new Date()
  const to = end.toISOString().slice(0, 10)
  let from: string
  switch (statsPeriodPreset.value) {
    case 'week':
      end.setDate(end.getDate() - 7)
      from = end.toISOString().slice(0, 10)
      break
    case 'quarter':
      end.setMonth(end.getMonth() - 3)
      from = end.toISOString().slice(0, 10)
      break
    case 'year':
      end.setFullYear(end.getFullYear() - 1)
      from = end.toISOString().slice(0, 10)
      break
    case 'month':
    default:
      end.setMonth(end.getMonth() - 1)
      from = end.toISOString().slice(0, 10)
      break
  }
  statsDateFrom.value = from
  statsDateTo.value = to
}

async function loadAdminStats() {
  if (statsPeriodPreset.value !== 'custom') setStatsDatesFromPreset()
  const dateFrom = statsDateFrom.value
  const dateTo = statsDateTo.value
  if (!dateFrom || !dateTo) return
  loadingStats.value = true
  try {
    const { data } = await api.get<AdminStatsData>('/stats/admin/', {
      params: {
        date_from: dateFrom,
        date_to: dateTo,
        basis: statsBasis.value,
      },
    })
    adminStats.value = data
    await nextTick()
    drawStatsCharts()
  } catch {
    adminStats.value = null
  } finally {
    loadingStats.value = false
  }
}

function formatKg(kg: number): string {
  if (kg == null) return '—'
  return `${Number(kg).toLocaleString('ru-RU')} кг`
}

function drawStatsCharts() {
  const data = adminStats.value
  if (!data) return
  const destroy = (c: Chart | null) => { c?.destroy() }

  if (viewModeMaterials.value === 'graph' && chartMaterialsRef.value && filteredMaterials.value.length) {
    destroy(chartMaterials)
    chartMaterials = new Chart(chartMaterialsRef.value, {
      type: 'bar',
      data: {
        labels: filteredMaterials.value.map(m => m.material_type_display),
        datasets: [{ label: 'Масса (кг)', data: filteredMaterials.value.map(m => m.total_kg), backgroundColor: 'rgba(25, 118, 210, 0.7)' }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    })
  } else { destroy(chartMaterials); chartMaterials = null }

  if (viewModeTopOrg.value === 'graph' && chartTopOrgRef.value && data.top_organizations.length) {
    destroy(chartTopOrg)
    const top10 = data.top_organizations.slice(0, 10)
    chartTopOrg = new Chart(chartTopOrgRef.value, {
      type: 'bar',
      data: {
        labels: top10.map(o => o.institution_name.length > 25 ? o.institution_name.slice(0, 22) + '…' : o.institution_name),
        datasets: [{ label: 'Масса (кг)', data: top10.map(o => o.total_kg), backgroundColor: 'rgba(56, 142, 60, 0.7)' }],
      },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } },
    })
  } else { destroy(chartTopOrg); chartTopOrg = null }

  if (viewModeStatus.value === 'graph' && chartStatusRef.value && data.requests_by_status.length) {
    destroy(chartStatus)
    chartStatus = new Chart(chartStatusRef.value, {
      type: 'doughnut',
      data: {
        labels: data.requests_by_status.map(s => s.status_display),
        datasets: [{ data: data.requests_by_status.map(s => s.count), backgroundColor: ['#ff9800', '#2196f3', '#4caf50'] }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    })
  } else { destroy(chartStatus); chartStatus = null }

  if (viewModeWeight.value === 'graph' && chartWeightRef.value && data.weight_over_time.length) {
    destroy(chartWeight)
    chartWeight = new Chart(chartWeightRef.value, {
      type: 'line',
      data: {
        labels: data.weight_over_time.map(w => w.period_label),
        datasets: [{ label: 'Масса (кг)', data: data.weight_over_time.map(w => w.total_kg), borderColor: '#1976d2', fill: true, tension: 0.2 }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    })
  } else { destroy(chartWeight); chartWeight = null }
}

watch(statsPeriodPreset, () => {
  if (statsPeriodPreset.value !== 'custom') setStatsDatesFromPreset()
})
watch([viewModeMaterials, viewModeTopOrg, viewModeStatus, viewModeWeight, filteredMaterials], () => {
  nextTick(() => drawStatsCharts())
})

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
    productForm.name = item.name
    productForm.description = item.description || ''
    productForm.price_in_points = parseFloat(item.price_in_points) || 0
    productForm.is_active = item.is_active
    if (item.image_url) productForm.imagePreview = item.image_url
  } else {
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
    const file = productForm.imageFile && productForm.imageFile.length ? productForm.imageFile[0] : null
    if (file) {
      const formData = new FormData()
      formData.append('name', productForm.name)
      formData.append('description', productForm.description)
      formData.append('price_in_points', String(productForm.price_in_points))
      formData.append('is_active', String(productForm.is_active))
      formData.append('image', file)
      // Do not set Content-Type: axios must set multipart/form-data with boundary so the server receives the file
      if (editingProduct.value) {
        await api.patch(`/products/${editingProduct.value.id}/`, formData)
      } else {
        await api.post('/products/', formData)
      }
    } else {
      const payload = {
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
    if (newsForm.imageFile && newsForm.imageFile.length > 0) {
      formData.append('image', newsForm.imageFile[0])
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
  if (item) {
    materialForm.name = item.name
    materialForm.code = item.code
    materialForm.is_active = item.is_active
  } else {
    materialForm.name = ''
    materialForm.code = ''
    materialForm.is_active = true
  }
  materialDialog.value = true
}

async function saveMaterial() {
  materialFormErrors.value = {}
  const name = (materialForm.name || '').trim()
  const code = (materialForm.code || '').trim().toLowerCase()
  if (!name) {
    materialFormErrors.value.name = 'Введите название'
    return
  }
  if (!code) {
    materialFormErrors.value.code = 'Введите код (латиница)'
    return
  }
  savingMaterial.value = true
  try {
    if (editingMaterial.value) {
      await api.patch(`/materials/${editingMaterial.value.id}/`, {
        name: name,
        is_active: materialForm.is_active,
      })
    } else {
      await api.post('/materials/', { name: name, code: code, is_active: materialForm.is_active })
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
  if (tab === 'registration-requests') loadRegistrationRequests()
  if (tab === 'requests') loadRequests()
  if (tab === 'statistics') {
    setStatsDatesFromPreset()
    // Advanced dashboard loads its own data via AdminStatsDashboard
  }
  if (tab === 'bonuses') {
    fetchBonusConfig()
    fetchInstitutionBonuses()
  }
  if (tab === 'products') loadProducts()
  if (tab === 'points-orders') loadPointsOrders()
})

watch(() => productForm.imageFile, (files) => {
  if (files && files.length && files[0] instanceof File) {
    productForm.imagePreview = URL.createObjectURL(files[0])
  }
})

onMounted(() => {
  loadPrices()
  loadMaterials()
})
</script>

<style scoped>
.admin-materials-search { min-width: 0; }
@media (max-width: 600px) {
  .admin-materials-table :deep(.v-data-table__td) { padding-left: 8px; padding-right: 8px; }
  .admin-dialog :deep(.v-card) { margin: 8px; max-height: calc(100vh - 16px); }
}
@media (max-width: 960px) {
  .vuvoz-tabs :deep(.v-tab) { min-width: 120px; }
  .v-main .v-container { padding-left: 12px; padding-right: 12px; }
}
</style>
