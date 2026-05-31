<template>
    <div class="flex min-h-screen bg-gray-100 font-sans">
      <Sidebar :userType="userType" />
  
      <div class="flex-1 ml-[200px] p-8 max-[768px]:ml-0 max-[768px]:pt-[70px]">
        <PageHeader title="Perfil" subtitle="Visualização de informações" />
  
        <div v-if="studentData" class="bg-white rounded-xl p-8 shadow-md flex gap-8 flex-wrap lg:flex-nowrap">
          <!-- Esquerda: Imagem e nome -->
          <ProfileImageCard :data="studentData" />
  
          <!-- Direita: Grid com 4 componentes -->
          <div class="w-full lg:w-3/5 grid grid-cols-1 lg:grid-cols-2 gap-8">
            <PersonalInfo :data="studentData" />
            <InterestsGoals :data="studentData" />
            <ChallengesSolutions :data="studentData" />
            <QuoteBlock :quote="studentData.quote" />
          </div>
        </div>
  
  
        <div v-else class="text-center text-gray-600 text-lg mt-20">A carregar perfil...</div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import Sidebar from '@/components/sidebar/Sidebar.vue'
  import PageHeader from '@/components/reusables/PageHeader.vue'
  import ProfileImageCard from '@/components/profile/ProfileImageCard.vue'
  import PersonalInfo from '@/components/profile/PersonalInfo.vue'
  import ChallengesSolutions from '@/components/profile/ChallengesSolutions.vue'
  import InterestsGoals from '@/components/profile/InterestsGoals.vue'
  import QuoteBlock from '@/components/profile/Quote.vue'
  import { useSessionStore } from '@/stores/session'
  import { getStudentById } from '@/api/studentAPI'
  import { getDirectorById } from '@/api/api'
  
  const session = useSessionStore()
  const userType = ref(session.type)
  const studentData = ref(null)
  
  onMounted(async () => {
    try {
      const id = Number(session.id)
      let data
  
      if (session.isStudent) {
        const student = await getStudentById(id)
        data = {
          id: student.number,
          name: student.name,
          profileImage: 'https://randomuser.me/api/portraits/women/44.jpg',
          age: student.age,
          location: student.city,
          profession: student.occupation,
          education: student.education,
          frequency: `Frequência do ${student.year}º ano do curso.`,
          interests: student.interests,
          objectives: student.goals,
          challenges: student.challenges,
          solutions: student.solutions,
          quote: student.quote
        }
      } else if (session.isDirector) {
        const director = await getDirectorById(id)
        data = {
          id: director.email,
          name: director.name,
          profileImage: 'https://randomuser.me/api/portraits/men/55.jpg',
          age: director.age,
          location: director.city,
          profession: director.occupation,
          education: director.education,
          frequency: '—',
          interests: director.interests,
          objectives: director.goals,
          challenges: director.challenges,
          solutions: director.solutions,
          quote: director.quote
        }
      }
  
      studentData.value = data
    } catch (err) {
      console.error('Erro ao buscar dados do utilizador:', err)
    }
  })
  </script>
  