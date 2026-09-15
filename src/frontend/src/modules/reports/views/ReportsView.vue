<template>
  <AppLayout>
    <!-- FILTER BAR -->
    <div
      class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 -mx-6 -mt-6 px-6 py-3 flex items-center gap-2 flex-wrap mb-0"
    >
      <button
        class="flex items-center gap-1 text-sm text-gray-600 border border-gray-300 rounded px-3 py-1.5 hover:bg-gray-50 transition font-medium"
      >
        FILTER
        <svg class="w-3 h-3" viewBox="0 0 10 6" fill="currentColor">
          <path d="M0 0l5 6 5-6z" />
        </svg>
      </button>
      <button
        v-for="f in filterOptions"
        :key="f"
        class="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded px-3 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-700 transition font-medium"
      >
        {{ f }}
        <svg
          class="w-3 h-3 text-gray-400"
          viewBox="0 0 10 6"
          fill="currentColor"
        >
          <path d="M0 0l5 6 5-6z" />
        </svg>
      </button>
      <div class="ml-auto">
        <button
          class="bg-blue-400 hover:bg-blue-500 text-white text-sm font-semibold px-5 py-1.5 rounded transition tracking-wide"
        >
          APPLY FILTER
        </button>
      </div>
    </div>

    <!-- SUMMARY BAR -->
    <div
      class="bg-gray-100 dark:bg-gray-800/60 border-b border-gray-200 dark:border-gray-700 -mx-6 px-6 py-3 flex items-center justify-between flex-wrap gap-3 mb-0"
    >
      <div class="text-sm text-gray-600 dark:text-gray-400">
        Total:
        <span class="font-bold text-gray-900 dark:text-gray-100 text-lg ml-1">{{
          totalFormatted
        }}</span>
      </div>
      <div class="flex items-center gap-4">
        <div class="relative">
          <button
            @click="exportOpen = !exportOpen"
            class="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-800 transition"
          >
            Export
            <svg class="w-3 h-3" viewBox="0 0 10 6" fill="currentColor">
              <path d="M0 0l5 6 5-6z" />
            </svg>
          </button>
          <div
            v-if="exportOpen"
            class="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10 min-w-[120px]"
          >
            <button
              v-for="fmt in ['PDF', 'CSV', 'Excel']"
              :key="fmt"
              class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition"
              @click="exportOpen = false"
            >
              Export as {{ fmt }}
            </button>
          </div>
        </div>
        <button class="text-gray-500 hover:text-gray-700 transition">
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4"
            />
          </svg>
        </button>
        <button class="text-gray-500 hover:text-gray-700 transition">
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
            />
          </svg>
        </button>
        <label class="flex items-center gap-2 cursor-pointer">
          <div class="relative w-9 h-5">
            <input type="checkbox" v-model="rounding" class="sr-only" />
            <div
              class="w-9 h-5 rounded-full transition"
              :class="rounding ? 'bg-blue-500' : 'bg-gray-300'"
            ></div>
            <div
              class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform"
              :class="rounding ? 'translate-x-4' : 'translate-x-0'"
            ></div>
          </div>
          <span class="text-sm text-gray-600">Rounding</span>
        </label>
      </div>
    </div>

    <!-- CHART -->
    <div class="bg-white border border-gray-200 rounded-lg mt-4 pb-4">
      <div class="px-4 pt-4 pb-2">
        <div class="relative inline-block">
          <button
            @click="groupChartOpen = !groupChartOpen"
            class="flex items-center gap-2 text-sm text-gray-700 border border-gray-300 rounded px-3 py-1.5 hover:bg-gray-50 transition"
          >
            {{ chartGroupBy }}
            <svg
              class="w-3 h-3 text-gray-400"
              viewBox="0 0 10 6"
              fill="currentColor"
            >
              <path d="M0 0l5 6 5-6z" />
            </svg>
          </button>
          <div
            v-if="groupChartOpen"
            class="absolute left-0 top-9 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10 min-w-[120px]"
          >
            <button
              v-for="opt in ['Project', 'Team', 'Client', 'Tag']"
              :key="opt"
              @click="
                chartGroupBy = opt;
                groupChartOpen = false;
              "
              class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition"
              :class="chartGroupBy === opt ? 'font-semibold text-blue-600' : ''"
            >
              {{ opt }}
            </button>
          </div>
        </div>
      </div>

      <div class="px-4 overflow-x-auto">
        <svg :width="chartWidth" :height="chartHeight" class="min-w-full">
          <g v-for="(tick, i) in yTicks" :key="'grid' + i">
            <line
              :x1="yAxisW"
              :y1="yPos(tick)"
              :x2="chartWidth"
              :y2="yPos(tick)"
              stroke="#e5e7eb"
              stroke-width="1"
              stroke-dasharray="4,4"
            />
            <text
              :x="yAxisW - 6"
              :y="yPos(tick) + 4"
              text-anchor="end"
              font-size="11"
              fill="#9ca3af"
            >
              {{ tick }}h
            </text>
          </g>
          <g v-for="(day, di) in weekData" :key="'bar' + di">
            <g v-if="day.total > 0">
              <g v-for="(seg, si) in day.segments" :key="'seg' + si">
                <rect
                  :x="barX(di)"
                  :y="segY(day, si)"
                  :width="barW"
                  :height="segH(day, si)"
                  :fill="seg.color"
                  rx="2"
                  class="cursor-pointer hover:opacity-80 transition-opacity"
                />
              </g>
              <text
                :x="barX(di) + barW / 2"
                :y="yPos(day.total) - 6"
                text-anchor="middle"
                font-size="11"
                fill="#374151"
                font-weight="500"
              >
                {{ formatHMS(day.total * 3600) }}
              </text>
            </g>
            <g v-else>
              <text
                :x="barX(di) + barW / 2"
                :y="yPos(0) - 6"
                text-anchor="middle"
                font-size="11"
                fill="#9ca3af"
              >
                00:00:00
              </text>
            </g>
            <text
              :x="barX(di) + barW / 2"
              :y="chartHeight - 4"
              text-anchor="middle"
              font-size="11"
              fill="#6b7280"
            >
              {{ day.label }}
            </text>
          </g>
        </svg>
      </div>
    </div>

    <!-- BOTTOM -->
    <div class="flex gap-4 mt-4">
      <div class="flex-1 min-w-0">
        <div
          class="bg-gray-100 border border-gray-200 rounded-t-lg px-4 py-2 flex items-center gap-3"
        >
          <span class="text-xs text-gray-500 font-medium">Group by:</span>
          <div class="relative">
            <button
              @click="groupBy1Open = !groupBy1Open"
              class="flex items-center gap-1 text-xs text-gray-700 border border-gray-300 bg-white rounded px-2.5 py-1 hover:bg-gray-50 transition"
            >
              {{ groupBy1 }}
              <svg class="w-2.5 h-2.5" viewBox="0 0 10 6" fill="currentColor">
                <path d="M0 0l5 6 5-6z" />
              </svg>
            </button>
            <div
              v-if="groupBy1Open"
              class="absolute left-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10 min-w-[120px]"
            >
              <button
                v-for="opt in ['Project', 'Team', 'Client', 'Tag', 'Status']"
                :key="opt"
                @click="
                  groupBy1 = opt;
                  groupBy1Open = false;
                "
                class="w-full text-left px-3 py-1.5 text-xs text-gray-700 hover:bg-gray-50"
                :class="groupBy1 === opt ? 'font-semibold text-blue-600' : ''"
              >
                {{ opt }}
              </button>
            </div>
          </div>
          <div class="relative">
            <button
              @click="groupBy2Open = !groupBy2Open"
              class="flex items-center gap-1 text-xs text-gray-700 border border-gray-300 bg-white rounded px-2.5 py-1 hover:bg-gray-50 transition"
            >
              {{ groupBy2 }}
              <svg class="w-2.5 h-2.5" viewBox="0 0 10 6" fill="currentColor">
                <path d="M0 0l5 6 5-6z" />
              </svg>
            </button>
            <div
              v-if="groupBy2Open"
              class="absolute left-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10 min-w-[120px]"
            >
              <button
                v-for="opt in ['Description', 'Task', 'Tag', 'Status']"
                :key="opt"
                @click="
                  groupBy2 = opt;
                  groupBy2Open = false;
                "
                class="w-full text-left px-3 py-1.5 text-xs text-gray-700 hover:bg-gray-50"
                :class="groupBy2 === opt ? 'font-semibold text-blue-600' : ''"
              >
                {{ opt }}
              </button>
            </div>
          </div>
        </div>

        <div
          class="bg-white border-x border-gray-200 px-4 py-2 flex items-center justify-between"
        >
          <div class="flex items-center gap-2">
            <button
              @click="allExpanded = !allExpanded"
              class="w-6 h-6 flex items-center justify-center bg-blue-500 rounded text-white text-xs hover:bg-blue-600 transition"
            >
              <svg
                class="w-3 h-3 transition-transform"
                :class="allExpanded ? '' : '-rotate-90'"
                viewBox="0 0 10 6"
                fill="currentColor"
              >
                <path d="M0 0l5 6 5-6z" />
              </svg>
            </button>
            <button
              @click="sortTitleDir *= -1"
              class="flex items-center gap-1 text-xs font-semibold text-gray-500 uppercase tracking-wide hover:text-gray-700"
            >
              TITLE
              <svg class="w-3 h-3" viewBox="0 0 10 14" fill="currentColor">
                <path
                  d="M5 0L9.33 5H0.67L5 0Z"
                  :opacity="sortTitleDir > 0 ? '1' : '0.4'"
                />
                <path
                  d="M5 14L0.67 9H9.33L5 14Z"
                  :opacity="sortTitleDir < 0 ? '1' : '0.4'"
                />
              </svg>
            </button>
          </div>
          <button
            class="flex items-center gap-1 text-xs font-semibold text-gray-500 uppercase tracking-wide hover:text-gray-700"
          >
            DURATION
            <svg class="w-3 h-3" viewBox="0 0 10 14" fill="currentColor">
              <path d="M5 0L9.33 5H0.67L5 0Z" />
              <path d="M5 14L0.67 9H9.33L5 14Z" opacity="0.4" />
            </svg>
          </button>
        </div>

        <div class="border border-gray-200 rounded-b-lg overflow-hidden">
          <div v-for="(group, gi) in sortedGroups" :key="gi">
            <div
              class="flex items-center justify-between px-4 py-3 bg-white border-t border-gray-100 cursor-pointer hover:bg-gray-50 transition"
              @click="toggleGroup(gi)"
            >
              <div class="flex items-center gap-3">
                <span
                  class="w-5 h-5 flex items-center justify-center bg-blue-500 text-white text-xs font-bold rounded"
                >
                  {{ group.entries.length }}
                </span>
                <span
                  class="w-2 h-2 rounded-full inline-block"
                  :style="{ background: group.color }"
                ></span>
                <span class="text-sm text-gray-700">{{ group.title }}</span>
              </div>
              <span class="text-sm font-mono text-gray-800 font-medium">{{
                formatHMS(group.totalSec)
              }}</span>
            </div>
            <div v-if="allExpanded || expandedGroups[gi]">
              <div
                v-for="(entry, ei) in group.entries"
                :key="ei"
                class="flex items-center justify-between px-4 py-2.5 bg-gray-50 border-t border-gray-100"
              >
                <div class="pl-10">
                  <p class="text-sm text-gray-700">{{ entry.desc }}</p>
                  <p class="text-xs text-gray-400 mt-0.5">{{ entry.date }}</p>
                </div>
                <span class="text-sm font-mono text-gray-600">{{
                  formatHMS(entry.durationSec)
                }}</span>
              </div>
            </div>
          </div>
          <div
            v-if="sortedGroups.length === 0"
            class="px-6 py-10 text-center text-sm text-gray-400"
          >
            No data for selected period.
          </div>
        </div>
      </div>

      <!-- Donut -->
      <div
        class="w-56 flex-shrink-0 bg-white border border-gray-200 rounded-lg p-4 flex flex-col items-center"
      >
        <svg width="160" height="160" viewBox="0 0 160 160">
          <g v-for="(seg, i) in donutSegments" :key="i">
            <path
              :d="seg.d"
              :fill="seg.color"
              class="hover:opacity-80 transition-opacity cursor-pointer"
            />
          </g>
          <circle cx="80" cy="80" r="48" fill="white" />
        </svg>
        <div class="mt-3 w-full space-y-2">
          <div
            v-for="(group, i) in tableGroups"
            :key="i"
            class="flex items-center gap-2 text-xs"
          >
            <span
              class="w-3 h-3 rounded-sm flex-shrink-0"
              :style="{ background: group.color }"
            ></span>
            <span class="text-gray-600 flex-1 truncate">{{ group.title }}</span>
            <span class="text-gray-700 font-medium"
              >{{ donutPct(group) }}%</span
            >
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import AppLayout from "../../../components/common/AppLayout.vue";
import type {
  TimeEntry,
  ChartDay,
  ChartSegment,
  ReportGroup,
  DonutSegment,
} from "../../../app/types/app.type";

const filterOptions: string[] = [
  "Team",
  "Client",
  "Project",
  "Task",
  "Tag",
  "Status",
  "Description",
];
const exportOpen = ref<boolean>(false);
const rounding = ref<boolean>(false);
const groupChartOpen = ref<boolean>(false);
const chartGroupBy = ref<string>("Project");
const groupBy1Open = ref<boolean>(false);
const groupBy2Open = ref<boolean>(false);
const groupBy1 = ref<string>("Project");
const groupBy2 = ref<string>("Description");
const allExpanded = ref<boolean>(false);
const expandedGroups = ref<Record<number, boolean>>({});
const sortTitleDir = ref<number>(1);

function toggleGroup(i: number): void {
  expandedGroups.value[i] = !expandedGroups.value[i];
}

const entries: TimeEntry[] = [
  {
    project: "FS Internship",
    color: "#2da58e",
    desc: "Fixing bugs in home screen",
    date: "Mon, Apr 6",
    daySec: 0,
    durationSec: 7629,
  },
  {
    project: "BE Internship",
    color: "#8b6f5e",
    desc: "Database schema design",
    date: "Mon, Apr 6",
    daySec: 0,
    durationSec: 9000,
  },
  {
    project: "FS Internship",
    color: "#2da58e",
    desc: "Adding theme feature",
    date: "Mon, Apr 6",
    daySec: 0,
    durationSec: 3600,
  },
  {
    project: "Without project",
    color: "#b0b8c1",
    desc: "Meeting standup",
    date: "Mon, Apr 6",
    daySec: 0,
    durationSec: 1200,
  },
  {
    project: "FS Internship",
    color: "#2da58e",
    desc: "Login page implementation",
    date: "Tue, Apr 7",
    daySec: 1,
    durationSec: 14400,
  },
  {
    project: "BE Internship",
    color: "#8b6f5e",
    desc: "API endpoint setup",
    date: "Tue, Apr 7",
    daySec: 1,
    durationSec: 14400,
  },
  {
    project: "FS Internship",
    color: "#2da58e",
    desc: "UI review & feedback",
    date: "Tue, Apr 7",
    daySec: 1,
    durationSec: 1800,
  },
  {
    project: "Open Source",
    color: "#6db33f",
    desc: "PR review",
    date: "Tue, Apr 7",
    daySec: 1,
    durationSec: 1628,
  },
  {
    project: "FS Internship",
    color: "#2da58e",
    desc: "Dashboard components",
    date: "Wed, Apr 8",
    daySec: 2,
    durationSec: 18000,
  },
  {
    project: "BE Internship",
    color: "#8b6f5e",
    desc: "Auth middleware",
    date: "Wed, Apr 8",
    daySec: 2,
    durationSec: 18000,
  },
  {
    project: "FS Internship",
    color: "#2da58e",
    desc: "Sidebar & routing",
    date: "Wed, Apr 8",
    daySec: 2,
    durationSec: 3600,
  },
  {
    project: "Without project",
    color: "#b0b8c1",
    desc: "Retrospective meeting",
    date: "Wed, Apr 8",
    daySec: 2,
    durationSec: 3010,
  },
  {
    project: "FS Internship",
    color: "#2da58e",
    desc: "Board kanban feature",
    date: "Thu, Apr 9",
    daySec: 3,
    durationSec: 18000,
  },
  {
    project: "BE Internship",
    color: "#8b6f5e",
    desc: "File upload service",
    date: "Thu, Apr 9",
    daySec: 3,
    durationSec: 18000,
  },
  {
    project: "FS Internship",
    color: "#2da58e",
    desc: "Chart integration",
    date: "Fri, Apr 10",
    daySec: 4,
    durationSec: 14400,
  },
  {
    project: "BE Internship",
    color: "#8b6f5e",
    desc: "Report API",
    date: "Fri, Apr 10",
    daySec: 4,
    durationSec: 14400,
  },
  {
    project: "FS Internship",
    color: "#2da58e",
    desc: "Polish & QA",
    date: "Fri, Apr 10",
    daySec: 4,
    durationSec: 3624,
  },
  {
    project: "Without project",
    color: "#b0b8c1",
    desc: "Team lunch",
    date: "Fri, Apr 10",
    daySec: 4,
    durationSec: 2160,
  },
];

const totalSec = computed<number>(() =>
  entries.reduce((s, e) => s + e.durationSec, 0),
);
const totalFormatted = computed<string>(() => formatHMS(totalSec.value));

function formatHMS(sec: number): string {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

const days: string[] = [
  "Mon, Apr 6",
  "Tue, Apr 7",
  "Wed, Apr 8",
  "Thu, Apr 9",
  "Fri, Apr 10",
  "Sat, Apr 11",
  "Sun, Apr 12",
];

const weekData = computed<ChartDay[]>(() =>
  days.map((d, i) => {
    const dayEntries = entries.filter((e) => e.daySec === i);
    const segMap: Record<string, { color: string; hours: number }> = {};
    dayEntries.forEach((e) => {
      if (!segMap[e.project]) segMap[e.project] = { color: e.color, hours: 0 };
      segMap[e.project].hours += e.durationSec / 3600;
    });
    const segments: ChartSegment[] = Object.entries(segMap).map(
      ([name, v]) => ({ name, color: v.color, hours: v.hours }),
    );
    const total = segments.reduce((s, seg) => s + seg.hours, 0);
    return {
      label: d.split(", ")[0] + ", " + d.split(", ")[1],
      segments,
      total,
    };
  }),
);

const chartWidth = 700;
const chartHeight = 340;
const yAxisW = 50;
const barW = 60;
const paddingTop = 40;
const paddingBot = 30;
const maxY = 36;
const yTicks: number[] = [5, 10, 15, 20, 25, 30, 35];

function yPos(val: number): number {
  const range = chartHeight - paddingTop - paddingBot;
  return paddingTop + range - (val / maxY) * range;
}
function barX(di: number): number {
  const slotW = (chartWidth - yAxisW) / 7;
  return yAxisW + di * slotW + (slotW - barW) / 2;
}
function segY(day: ChartDay, si: number): number {
  const above = day.segments.slice(si + 1).reduce((s, seg) => s + seg.hours, 0);
  return yPos(above + day.segments[si].hours);
}
function segH(day: ChartDay, si: number): number {
  return yPos(0) - yPos(day.segments[si].hours);
}

const tableGroups = computed<ReportGroup[]>(() => {
  const map: Record<string, ReportGroup> = {};
  entries.forEach((e) => {
    if (!map[e.project])
      map[e.project] = {
        title: e.project,
        color: e.color,
        totalSec: 0,
        entries: [],
      };
    map[e.project].totalSec += e.durationSec;
    map[e.project].entries.push({
      desc: e.desc,
      date: e.date,
      durationSec: e.durationSec,
    });
  });
  return Object.values(map);
});

const sortedGroups = computed<ReportGroup[]>(() =>
  [...tableGroups.value].sort(
    (a, b) => sortTitleDir.value * a.title.localeCompare(b.title),
  ),
);

const donutSegments = computed<DonutSegment[]>(() => {
  const cx = 80,
    cy = 80,
    r = 70,
    hole = 48;
  const total = tableGroups.value.reduce((s, g) => s + g.totalSec, 0);
  let angle = -Math.PI / 2;
  return tableGroups.value.map((group) => {
    const sweep = (group.totalSec / total) * 2 * Math.PI;
    const x1 = cx + r * Math.cos(angle),
      y1 = cy + r * Math.sin(angle);
    angle += sweep;
    const x2 = cx + r * Math.cos(angle),
      y2 = cy + r * Math.sin(angle);
    const xi1 = cx + hole * Math.cos(angle - sweep),
      yi1 = cy + hole * Math.sin(angle - sweep);
    const xi2 = cx + hole * Math.cos(angle),
      yi2 = cy + hole * Math.sin(angle);
    const large = sweep > Math.PI ? 1 : 0;
    const d = `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} L ${xi2} ${yi2} A ${hole} ${hole} 0 ${large} 0 ${xi1} ${yi1} Z`;
    return { d, color: group.color };
  });
});

function donutPct(group: ReportGroup): number {
  const total = tableGroups.value.reduce((s, g) => s + g.totalSec, 0);
  return Math.round((group.totalSec / total) * 100);
}
</script>
